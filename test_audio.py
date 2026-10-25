import asyncio
import numpy as np
import sounddevice as sd
import soundfile as sf
from shazamio import Shazam

FICHIER_TEMP = "sample.wav"
DUREE = 5
SAMPLE_RATE = 44100

def enregistrer():
    print(f"\n[1/2] Écoute pendant {DUREE} secondes (mets la musique maintenant)...")
    audio = sd.rec(int(DUREE * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    
    # Vérification du volume capté
    volume_max = np.max(np.abs(audio))
    print(f"-> Niveau sonore capté (max) : {volume_max} / 32767")
    if volume_max < 500:
        print("⚠️ Le micro n'a quasiment rien capté (son trop faible ou micro coupé).")
    
    sf.write(FICHIER_TEMP, audio, SAMPLE_RATE)
    print("-> Fichier sample.wav enregistré.")

async def analyser():
    print("[2/2] Envoi à Shazam...")
    try:
        shazam = Shazam()
        resultat = await shazam.recognize(FICHIER_TEMP)
        track = resultat.get("track")
        if not track:
            print("\n❌ Aucun morceau reconnu.")
            return

        print("\n✅ Morceau trouvé !")
        print(f"🎵 Titre   : {track.get('title')}")
        print(f"👤 Artiste : {track.get('subtitle')}")
    except Exception as e:
        print(f"\n❌ Erreur pendant l'analyse : {e}")

if __name__ == "__main__":
    enregistrer()
    asyncio.run(analyser())
