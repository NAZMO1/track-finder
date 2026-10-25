FROM python:3.12-slim

# Empêche Python d'écrire des fichiers .pyc et force l'affichage direct des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances C et audio système nécessaires (ffmpeg pour pydub/shazamio)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installation des paquets Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code applicatif
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
