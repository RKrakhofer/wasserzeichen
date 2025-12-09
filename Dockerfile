# Multi-stage build für optimale Image-Größe
FROM python:3.12-slim

# Setze Arbeitsverzeichnis
WORKDIR /app

# Installiere System-Abhängigkeiten für Pillow und Schriftarten
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Kopiere requirements zuerst (für besseres Caching)
COPY requirements.txt .

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere Anwendungscode
COPY app.py .
COPY watermark.py .
COPY templates/ templates/
COPY static/ static/

# Erstelle Upload-Verzeichnis
RUN mkdir -p uploads

# Exponiere Port
EXPOSE 5000

# Setze Umgebungsvariablen
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Starte Flask-App
CMD ["python", "app.py"]
