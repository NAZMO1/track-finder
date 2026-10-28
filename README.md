# 🎵 Track Finder

**Application web de reconnaissance musicale — FastAPI · ShazamIO · SQLite · Docker**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

Track Finder est un prototype full-stack inspiré du principe de Shazam : il enregistre **5 secondes d'audio depuis le navigateur**, identifie un morceau avec **ShazamIO**, présente ses informations et conserve un historique local.

## ✨ Fonctionnalités

- Capture microphone avec `getUserMedia` et `MediaRecorder`, compte à rebours de 5 secondes.
- Identification du titre, de l'artiste et récupération de la pochette si disponibles.
- Liens de recherche vers **Spotify** et **YouTube** ; lien Apple Music si fourni par le service.
- Historique **SQLite** des reconnaissances, affichant les **10 dernières entrées**.
- API HTTP **FastAPI**, interface web intégrée et démarrage via **Docker Compose**.

## 🧱 Architecture

```text
Navigateur (HTML / CSS / JavaScript)
      │ microphone → MediaRecorder
      ▼
POST /recognize (fichier audio)
      │
      ▼
FastAPI → ShazamIO → métadonnées musicales
      │
      ├── réponse JSON → affichage du résultat
      └── SQLAlchemy → SQLite (table history)

GET /history → dernières reconnaissances
```

| Composant | Technologies |
| --- | --- |
| Frontend | HTML, CSS, JavaScript natif |
| Backend | Python, FastAPI, Uvicorn |
| Reconnaissance | ShazamIO |
| Base de données | SQLite, SQLAlchemy |
| Environnement | Docker, Docker Compose, FFmpeg |

## 🚀 Installation avec Docker

**Prérequis :** Docker et Docker Compose.

```bash
git clone https://github.com/NAZMO1/track-finder.git
cd track-finder
docker compose up --build
```

Ouvrir **http://localhost:8000**, autoriser le microphone et cliquer sur *Lancer l'écoute (5s)*.

Arrêter avec `docker compose down`. Le volume `.:/app` du fichier Compose conserve le fichier SQLite dans le dossier du projet.

## 💻 Installation sans Docker

Prévoir **Python 3.12** et **FFmpeg** dans le PATH.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell : .venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn main:app --reload
```

Application : **http://127.0.0.1:8000** · Documentation interactive : **http://127.0.0.1:8000/docs**

L'autorisation d'accès au microphone est indispensable. Un déploiement web distant requiert généralement HTTPS pour l'accès micro.

## 🔌 API

| Méthode | Route | Description |
| --- | --- | --- |
| GET | `/` | Interface de l'application |
| POST | `/recognize` | Analyse d'un fichier audio (champ `file` en multipart) |
| GET | `/history` | Historique des 10 dernières identifications |

```bash
curl -X POST http://localhost:8000/recognize -F "file=@extrait.webm"
```

La réponse à une reconnaissance réussie contient `status: "success"` et les métadonnées. Sinon, elle renvoie `status: "not_found"`.

## 📁 Organisation

```text
track-finder/
├── main.py             # API, frontend et accès SQLite
├── requirements.txt    # Dépendances de l'application
├── Dockerfile          # Image Python et FFmpeg
├── docker-compose.yml  # Service web sur le port 8000
├── test_audio.py       # Test indépendant de reconnaissance audio
└── README.md
```

Pour exécuter `test_audio.py`, installer aussi `numpy`, `sounddevice` et `soundfile`, qui ne figurent pas dans le fichier de dépendances principal.

## 🧠 Compétences mises en pratique

Intégration d'API, capture audio côté navigateur, routes HTTP, traitement asynchrone, modélisation de données avec SQLAlchemy et conteneurisation d'une application Python.

## ⚠️ Limites et pistes d'amélioration

Ce projet est un **prototype pédagogique** : il utilise ShazamIO et ne met pas en œuvre son propre algorithme d'empreinte acoustique. La reconnaissance dépend d'un service externe et des conditions sonores. L'historique est local, sans authentification. L'API n'est pas encore préparée pour une exposition publique.

- [ ] Ajouter des tests automatisés et une validation stricte des fichiers envoyés.
- [ ] Ajouter recherche, pagination et suppression de l'historique.
- [ ] Améliorer les messages d'erreur et le traitement des exceptions.
- [ ] Ajouter captures d'écran, démonstration et déploiement HTTPS.

---

**Projet personnel : développement full-stack, reconnaissance audio et Docker.**
