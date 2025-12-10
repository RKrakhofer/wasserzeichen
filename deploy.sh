#!/bin/bash
# Deployment-Script für wasserzeichen auf uu@stage

set -e  # Beende bei Fehler

# Konfiguration
REMOTE_USER="uu"
REMOTE_HOST="stage"
REMOTE_DIR="/home/uu/wasserzeichen"
LOCAL_DIR="."

echo "🚀 Deployment zu $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
echo ""

# 1. Erstelle Remote-Verzeichnis falls nicht vorhanden
echo "📁 Erstelle Verzeichnis auf Server..."
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_DIR"

# 2. Kopiere Dateien via rsync
echo "📤 Kopiere Dateien..."
rsync -avz --progress \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='uploads/*' \
  --exclude='*.jpg' \
  --exclude='*.png' \
  --exclude='*.jpeg' \
  --exclude='.idea' \
  --exclude='.vscode' \
  $LOCAL_DIR/ $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

# 3. Baue und starte Docker Container auf dem Server
echo "🐳 Baue neues Image..."
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_DIR && docker compose build"

echo "⚠️  Hinweis: Container läuft weiter (AppArmor-Problem beim Stoppen)"
echo "   Für Neustart des Containers: Server-Neustart nötig oder manuell:"
echo "   ssh uu@stage 'sudo systemctl restart docker'
"

# 4. Zeige Status
echo ""
echo "✅ Deployment abgeschlossen!"
echo ""
echo "🌐 App sollte verfügbar sein unter: http://stage:5000"
echo ""
echo "📊 Container Status:"
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_DIR && docker compose ps"

echo ""
echo "📜 Logs anzeigen:"
echo "   ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_DIR && docker compose logs -f'"
