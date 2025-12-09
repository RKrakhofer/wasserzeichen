# Wasserzeichen-Tool für Bilder

Ein Python-Tool zum Hinzufügen von diagonalen, halbtransparenten Text-Wasserzeichen zu Bildern.
Verfügbar als **Kommandozeilen-Tool** und **Web-App**.

## Features

- ✨ Diagonales Wasserzeichen über das gesamte Bild
- 🔤 Automatische ein- oder zweizeilige Textformatierung
- 📏 Adaptive Schriftgröße - Text reicht von Ecke zu Ecke
- 🎨 Anpassbare Transparenz und Textfarbe
- 💾 Intelligente Dateinamen
- 🌐 Moderne Web-Oberfläche mit Drag & Drop
- 🎨 Color Picker für Farbauswahl
- 📱 Responsive Design
- 🐳 Docker-Support

## Installation

### Option 1: Docker (empfohlen)

**Voraussetzungen:**
- Docker
- Docker Compose

**Schnellstart:**

```bash
# Mit Docker Compose
docker-compose up -d

# Oder manuell
docker build -t watermark-app .
docker run -d -p 5000:5000 watermark-app
```

Die Web-App ist dann verfügbar unter: `http://localhost:5000`

**Container stoppen:**
```bash
docker-compose down
```

### Option 2: Lokale Installation

**Voraussetzungen:**
- Python 3.8 oder höher
- pip (Python Package Manager)

**Setup:**

1. Repository klonen oder herunterladen
2. Virtuelle Umgebung erstellen und aktivieren:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Auf Linux/Mac
# oder
.venv\Scripts\activate  # Auf Windows
```

3. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

## Verwendung

### Web-App (empfohlen)

1. Web-Server starten:

```bash
python app.py
```

2. Browser öffnen: `http://localhost:5000`

3. Bild hochladen:
   - Per Drag & Drop in den Upload-Bereich ziehen
   - Oder auf "Datei auswählen" klicken

4. Wasserzeichen-Text eingeben

5. Optional: Transparenz anpassen (0-100%)

6. "Wasserzeichen hinzufügen" klicken

7. Vorschau ansehen und Bild herunterladen

### Kommandozeilen-Tool

```bash
python watermark.py <bilddatei> "<wasserzeichen-text>"
```

### Beispiele

```bash
# Einfaches Wasserzeichen
python watermark.py foto.jpg "Copyright 2025"

# Mit benutzerdefinierter Transparenz
python watermark.py bild.png "Vertraulich - Nicht weitergeben" --opacity 100

# Mit roter Schrift
python watermark.py bild.jpg "ENTWURF" --color "#FF0000" --opacity 180

# Längerer Text (wird automatisch zweizeilig formatiert)
python watermark.py landschaft.jpg "Foto von Max Mustermann - Alle Rechte vorbehalten"
```

### Parameter

- `image` (erforderlich): Pfad zur Eingabe-Bilddatei
- `text` (erforderlich): Text für das Wasserzeichen
- `--opacity` (optional): Transparenz des Wasserzeichens
  - Bereich: 0-255
  - 0 = unsichtbar
  - 128 = 50% transparent (Standard)
  - 255 = komplett undurchsichtig
- `--color` (optional): Textfarbe als Hex-Wert
  - Format: #RRGGBB (z.B. #FFFFFF für Weiß, #FF0000 für Rot)
  - Standard: #FFFFFF (Weiß)

## Ausgabe

Das modifizierte Bild wird gespeichert als:
```
<originalbildname>-<text-kurzfassung>.jpg
```

Beispiele:
- Eingabe: `foto.jpg`, Text: `"Copyright 2025"`
- Ausgabe: `foto-copyright_2025.jpg`

- Eingabe: `bild.png`, Text: `"Mein Wasserzeichen"`
- Ausgabe: `bild-mein_wasserzeichen.jpg`

## Funktionsweise

1. **Textformatierung**: 
   - Texte bis 30 Zeichen: einzeilig
   - Längere Texte: zweizeilig (intelligente Trennung an Wortgrenzen)

2. **Wasserzeichen-Positionierung**:
   - Diagonal über das gesamte Bild
   - Automatische Winkelberechnung basierend auf Bildproportionen
   - Zentriert platziert

3. **Adaptive Schriftgröße**:
   - Binäre Suche für optimale Größe
   - Text füllt ca. 85% der Bilddiagonale
   - Kurze Texte werden größer dargestellt
   - Verhindert Überlauf aus dem Bild

4. **Speicherung**:
   - Format: JPEG mit hoher Qualität (95%)
   - Automatische Konvertierung von RGBA zu RGB

## Unterstützte Bildformate

- JPEG/JPG
- PNG
- BMP
- GIF
- TIFF
- und alle weiteren von Pillow unterstützten Formate

## Projektstruktur

```
wasserzeichen/
├── app.py              # Flask Web-App
├── watermark.py        # Kommandozeilen-Tool
├── requirements.txt    # Python-Abhängigkeiten
├── README.md          # Diese Datei
├── REQUIREMENTS.md    # Detaillierte Anforderungen
├── templates/
│   └── index.html     # Web-Interface
├── static/
│   ├── style.css      # Styling
│   └── script.js      # Frontend-Logik
└── .venv/            # Virtuelle Umgebung
```

## Technologie-Stack

- **Backend**: Flask (Python Web-Framework)
- **Bildverarbeitung**: Pillow (PIL Fork)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Features**: Drag & Drop API, FileReader API, Fetch API
- **Deployment**: Docker & Docker Compose

## Lizenz

Dieses Projekt steht zur freien Verwendung zur Verfügung.

## Troubleshooting

### Docker: Container startet nicht

Überprüfen Sie die Logs:
```bash
docker-compose logs -f
```

Stellen Sie sicher, dass Port 5000 nicht bereits belegt ist:
```bash
# Anderen Port verwenden
docker run -d -p 8080:5000 watermark-app
```

### Web-App: Port bereits in Verwendung

Falls Port 5000 bereits belegt ist, ändern Sie in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Verwende Port 8080 statt 5000
```

Oder in `app.py` (bei lokaler Installation):
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Anderen Port verwenden
```

### Schriftart nicht gefunden

Das Script versucht automatisch verschiedene Systemschriftarten zu laden. Falls keine gefunden wird, wird eine Standard-Schrift verwendet. Für beste Ergebnisse sollten folgende Schriftarten installiert sein:

- **Linux**: DejaVu Sans oder Liberation Sans
- **Windows**: Arial (meist vorinstalliert)
- **macOS**: Helvetica (meist vorinstalliert)

### Fehler beim Öffnen des Bildes

Stellen Sie sicher, dass:
- Der Dateipfad korrekt ist
- Die Datei tatsächlich ein Bild ist
- Sie Leserechte für die Datei haben
