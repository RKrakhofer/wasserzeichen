# Anforderungen - Wasserzeichen-Tool

## Funktionale Anforderungen

### FR-1: Eingabeparameter
- Das Script muss zwei Pflichtparameter akzeptieren:
  1. Pfad zu einer Bilddatei
  2. Text-String für das Wasserzeichen
- Optionale Parameter:
  - `--opacity`: Transparenz (0-255)
  - `--color`: Textfarbe als Hex-Wert (z.B. #FFFFFF)

### FR-2: Textformatierung
- Der Text soll intelligent formatiert werden:
  - Kurze Texte (≤30 Zeichen): einzeilig
  - Längere Texte: zweizeilig mit Trennung an sinnvollen Wortgrenzen
- Die Trennung soll möglichst in der Textmitte erfolgen

### FR-3: Wasserzeichen-Eigenschaften
- **Position**: Diagonal über das gesamte Bild
- **Transparenz**: Halbtransparent (Standard: 50%, anpassbar)
- **Farbe**: Konfigurierbar (Standard: Weiß #FFFFFF)
- **Schriftgröße**: Adaptiv - Text füllt ca. 85% der Bilddiagonale
- **Ausrichtung**: Zentriert auf dem Bild
- **Skalierung**: Binäre Suche für optimale Schriftgröße

### FR-4: Ausgabedatei
- Dateiformat: JPEG
- Dateiname-Schema: `<originalbildname>-<text-kurzfassung>.jpg`
- Kurzfassung des Textes:
  - Maximal 20 Zeichen
  - Nur alphanumerische Zeichen
  - Leerzeichen werden zu Unterstrichen
  - Kleinschreibung
- Qualität: Hoch (95%)

### FR-5: Fehlerbehandlung
- Validierung der Eingabedatei (Existenz, Lesbarkeit)
- Aussagekräftige Fehlermeldungen bei:
  - Fehlender Bilddatei
  - Ungültiger Bilddatei
  - Schreibfehlern
  - Sonstigen Verarbeitungsfehlern

### FR-6: Web-Interface
- Moderne Web-App mit Flask-Backend
- Drag & Drop für Bild-Upload
- Live-Vorschau des Originalbilds und Wasserzeichens
- Interaktive Steuerungen:
  - Textfeld für Wasserzeichen-Text
  - Transparenz-Slider mit Prozentanzeige
  - Color Picker mit Hex-Wert-Anzeige
- Download-Button für verarbeitetes Bild
- Fehlerbehandlung mit Benutzer-Feedback
- Loading-Animation während Verarbeitung

## Nicht-funktionale Anforderungen

### NFR-1: Benutzerfreundlichkeit
- Klare Kommandozeilen-Hilfe (`--help`)
- Fortschrittsinformationen während der Verarbeitung
- Erfolgsbestätigung mit Pfad zur Ausgabedatei

### NFR-2: Kompatibilität
- **Python-Version**: 3.8 oder höher
- **Betriebssysteme**: Linux, macOS, Windows
- **Bildformate**: Alle von Pillow unterstützten Formate (JPEG, PNG, BMP, GIF, TIFF, etc.)

### NFR-3: Performance
- Effiziente Bildverarbeitung auch bei großen Bildern
- Speichereffiziente Handhabung von RGBA/RGB-Konvertierungen

### NFR-4: Wartbarkeit
- Gut strukturierter, kommentierter Code
- Modulare Funktionen mit klar definierten Verantwortlichkeiten
- Type Hints für bessere Code-Dokumentation

### NFR-5: Skalierbarkeit
- Automatische Anpassung der Schriftgröße an verschiedene Bildgrößen
- Dynamische Berechnung des Rotationswinkels basierend auf Bildproportionen

## Technische Anforderungen

### TR-1: Abhängigkeiten
- **Pillow (PIL)**: ≥10.0.0 für Bildverarbeitung
- **Flask**: ≥3.0.0 für Web-App
- **Werkzeug**: ≥3.0.0 für sichere Datei-Uploads
- Standard-Python-Bibliotheken:
  - `argparse`: Kommandozeilen-Argument-Parsing
  - `pathlib`: Dateipfad-Handhabung
  - `math`: Winkelberechnungen
  - `sys`: Fehlerausgabe
  - `io`: BytesIO für Bild-Streaming
  - `base64`: Bild-Kodierung für Web-Transfer

### TR-2: Virtuelle Umgebung
- Verwendung einer Python Virtual Environment (`.venv`)
- Isolation von Projekt-Abhängigkeiten
- `requirements.txt` für Dependency Management

### TR-3: Schriftarten
- Unterstützung für System-Schriftarten
- Fallback-Mechanismus bei fehlenden Schriftarten:
  1. DejaVu Sans Bold (Linux)
  2. Liberation Sans Bold (Linux)
  3. Standard-Schriftart (Fallback)

### TR-4: Deployment
- Docker-Unterstützung für einfaches Deployment
- Multi-stage Dockerfile für optimale Image-Größe
- Docker Compose für Ein-Befehl-Start
- Automatisches Schriftarten-Setup im Container
- Volume-Mapping für persistente Uploads (optional)

## Designentscheidungen

### DD-1: Wasserzeichen-Algorithmus
1. Bild in RGBA konvertieren (für Transparenz)
2. Transparentes Overlay erstellen
3. Text auf rotiertem temporären Bild zeichnen
4. Rotiertes Bild über Original legen
5. Für JPEG-Ausgabe: RGBA zu RGB konvertieren mit weißem Hintergrund

### DD-2: Winkelberechnung
- Winkel = arctan(Höhe / Breite) des Bildes
- Gewährleistet optimale diagonale Ausrichtung für jedes Seitenverhältnis

### DD-3: Dateinamen-Generierung
- Entfernung von Sonderzeichen verhindert Dateisystem-Probleme
- Begrenzung auf 20 Zeichen verhindert zu lange Dateinamen
- Kleinschreibung für Konsistenz

### DD-4: Farbkonvertierung
- Hex-Eingabe (#RRGGBB) wird zu RGB-Tupel konvertiert
- Unterstützung für alle 16.7 Millionen Farben
- Validierung des Hex-Formats

### DD-5: Adaptive Schriftgröße
- Binäre Suche für optimale Schriftgröße (max. 15 Iterationen)
- Zielbreite: 85% der Bilddiagonale
- Berücksichtigung der längsten Textzeile
- Verhindert Überlauf aus dem Bildbereich

## Zukünftige Erweiterungen (Optional)

### Implementiert ✓
- [x] Konfigurierbare Wasserzeichen-Farbe
- [x] Web-App / GUI-Interface
- [x] Docker-Deployment
- [x] Adaptive Schriftgröße (Ecke zu Ecke)

### Noch offen
- [ ] Verschiedene Positionierungen (Ecken, zentriert, kachelnd)
- [ ] Batch-Verarbeitung mehrerer Bilder
- [ ] Bildformat-Auswahl für Ausgabe
- [ ] Mehrsprachige Fehlermeldungen
- [ ] Logo/Bild als Wasserzeichen statt Text
- [ ] Konfigurationsdatei für Standard-Einstellungen
