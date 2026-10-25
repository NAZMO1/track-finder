import os
import shutil
import urllib.parse
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from shazamio import Shazam
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "sqlite:///./tracks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TrackHistory(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String)
    cover_url = Column(String)
    detected_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Track Finder API")
shazam = Shazam()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Track Finder</title>
    <style>
        body { font-family: system-ui, sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; margin: 0; background: #0f172a; color: white; padding: 2rem 1rem; }
        .card { background: #1e293b; padding: 2.5rem; border-radius: 1rem; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; max-width: 480px; width: 100%; margin-bottom: 2rem; }
        button.record-btn { background: #0284c7; color: white; border: none; padding: 1rem 2rem; font-size: 1.1rem; border-radius: 9999px; cursor: pointer; transition: 0.2s; font-weight: bold; }
        button.record-btn:hover { background: #0369a1; }
        button.record-btn:disabled { background: #475569; cursor: not-allowed; }
        #status { margin-top: 1.5rem; font-size: 0.95rem; color: #94a3b8; }
        #result { margin-top: 1.5rem; display: none; }
        #cover { width: 160px; height: 160px; border-radius: 0.75rem; object-fit: cover; margin-bottom: 0.8rem; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
        h2 { margin: 0.3rem 0; font-size: 1.2rem; }
        p.artist { margin: 0 0 1rem 0; color: #38bdf8; font-weight: 500; }
        
        .streaming-links { display: flex; justify-content: center; gap: 0.6rem; flex-wrap: wrap; margin-top: 1rem; }
        .stream-btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 0.9rem; border-radius: 0.5rem; font-size: 0.85rem; text-decoration: none; font-weight: 600; color: white; transition: 0.2s; }
        .spotify-btn { background: #1db954; }
        .youtube-btn { background: #ef4444; }
        .apple-btn { background: #fa2d48; }
        .stream-btn:hover { opacity: 0.85; }

        .history-box { max-width: 480px; width: 100%; background: #1e293b; border-radius: 1rem; padding: 1.5rem; box-sizing: border-box; }
        .history-title { font-size: 1.1rem; margin-top: 0; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }
        .track-item { display: flex; align-items: center; gap: 1rem; padding: 0.7rem 0; border-bottom: 1px solid #334155; }
        .track-item img { width: 45px; height: 45px; border-radius: 6px; object-fit: cover; }
        .track-info { text-align: left; overflow: hidden; flex: 1; }
        .track-info b { font-size: 0.95rem; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .track-info span { font-size: 0.8rem; color: #94a3b8; }
    </style>
</head>
<body>
    <div class="card">
        <h1 style="margin-top: 0;">🎵 Track Finder</h1>
        <p style="color: #cbd5e1; margin-bottom: 1.5rem;">Reconnaissance acoustique instantanée</p>
        
        <button id="recordBtn" class="record-btn" onclick="startRecognition()">Lancer l'écoute (5s)</button>
        <div id="status">Prêt à écouter</div>

        <div id="result">
            <img id="cover" src="" alt="Cover">
            <h2 id="title">Titre</h2>
            <p class="artist" id="artist">Artiste</p>
            
            <div class="streaming-links">
                <a id="spotifyLink" href="#" target="_blank" class="stream-btn spotify-btn">Spotify</a>
                <a id="youtubeLink" href="#" target="_blank" class="stream-btn youtube-btn">YouTube</a>
                <a id="appleLink" href="#" target="_blank" class="stream-btn apple-btn" style="display:none;">Apple Music</a>
            </div>
        </div>
    </div>

    <div class="history-box">
        <h3 class="history-title">🕒 Historique des découvertes</h3>
        <div id="historyList">Chargement...</div>
    </div>

    <script>
        async function fetchHistory() {
            const res = await fetch("/history");
            const data = await res.json();
            const list = document.getElementById("historyList");
            if (!data.length) {
                list.innerHTML = "<p style='color:#64748b; font-size:0.9rem;'>Aucun morceau dans l'historique.</p>";
                return;
            }
            list.innerHTML = data.map(t => `
                <div class="track-item">
                    <img src="${t.cover_url || 'https://via.placeholder.com/45'}" alt="cover">
                    <div class="track-info">
                        <b>${t.title}</b>
                        <span>${t.artist}</span>
                    </div>
                </div>
            `).join('');
        }

        async function startRecognition() {
            const btn = document.getElementById("recordBtn");
            const status = document.getElementById("status");
            const resultBox = document.getElementById("result");

            resultBox.style.display = "none";
            btn.disabled = true;

            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const mediaRecorder = new MediaRecorder(stream);
                const chunks = [];

                mediaRecorder.ondataavailable = e => chunks.push(e.data);

                mediaRecorder.onstop = async () => {
                    status.innerText = "⏳ Analyse acoustique et enregistrement...";
                    const audioBlob = new Blob(chunks, { type: 'audio/webm' });
                    const formData = new FormData();
                    formData.append("file", audioBlob, "recording.webm");

                    try {
                        const res = await fetch("/recognize", { method: "POST", body: formData });
                        const data = await res.json();

                        if (data.status === "success") {
                            document.getElementById("title").innerText = data.track.title;
                            document.getElementById("artist").innerText = data.track.subtitle;
                            document.getElementById("cover").src = data.track.cover;

                            // Liens de streaming
                            document.getElementById("spotifyLink").href = data.track.spotify_url;
                            document.getElementById("youtubeLink").href = data.track.youtube_url;
                            
                            const appleLink = document.getElementById("appleLink");
                            if (data.track.apple_url) {
                                appleLink.href = data.track.apple_url;
                                appleLink.style.display = "inline-flex";
                            } else {
                                appleLink.style.display = "none";
                            }

                            resultBox.style.display = "block";
                            status.innerText = "✅ Morceau identifié et archivé !";
                            fetchHistory();
                        } else {
                            status.innerText = "❌ Aucun morceau reconnu.";
                        }
                    } catch (err) {
                        status.innerText = "Erreur de communication avec l'API.";
                    } finally {
                        btn.disabled = false;
                        stream.getTracks().forEach(track => track.stop());
                    }
                };

                mediaRecorder.start();
                let countdown = 5;
                status.innerText = `Écoute en cours... (${countdown}s)`;
                
                const interval = setInterval(() => {
                    countdown--;
                    if (countdown > 0) {
                        status.innerText = `Écoute en cours... (${countdown}s)`;
                    } else {
                        clearInterval(interval);
                        mediaRecorder.stop();
                    }
                }, 1000);

            } catch (err) {
                status.innerText = "❌ Accès micro refusé dans le navigateur.";
                btn.disabled = false;
            }
        }

        fetchHistory();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_CONTENT

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(TrackHistory).order_by(TrackHistory.detected_at.desc()).limit(10).all()

@app.post("/recognize")
async def recognize_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = await shazam.recognize(temp_path)
        track = result.get("track")
        
        if not track:
            return {"status": "not_found"}

        title = track.get("title", "Inconnu")
        artist = track.get("subtitle", "Inconnu")
        cover = track.get("images", {}).get("coverart", "")

        # Génération des liens de recherche directs
        query = urllib.parse.quote(f"{title} {artist}")
        spotify_url = f"https://open.spotify.com/search/{query}"
        youtube_url = f"https://www.youtube.com/results?search_query={query}"
        
        # Lien Apple Music officiel fourni par Shazam si dispo
        apple_url = track.get("hub", {}).get("options", [{}])[0].get("actions", [{}])[-1].get("uri", "")

        # Sauvegarde SQLite
        record = TrackHistory(title=title, artist=artist, cover_url=cover)
        db.add(record)
        db.commit()

        return {
            "status": "success",
            "track": {
                "title": title,
                "subtitle": artist,
                "cover": cover,
                "spotify_url": spotify_url,
                "youtube_url": youtube_url,
                "apple_url": apple_url
            }
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
