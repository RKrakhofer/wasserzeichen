#!/usr/bin/env python3
"""
Wasserzeichen-Script für Bilder
Fügt diagonalen, halbtransparenten Text als Wasserzeichen zu Bildern hinzu.
"""

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math


def create_short_name(text: str, max_length: int = 20) -> str:
    """
    Erstellt eine Kurzfassung des Textes für den Dateinamen.
    
    Args:
        text: Der ursprüngliche Text
        max_length: Maximale Länge der Kurzfassung
        
    Returns:
        Kurzfassung des Textes (nur alphanumerische Zeichen)
    """
    # Entferne Sonderzeichen und ersetze Leerzeichen mit Unterstrichen
    short = "".join(c if c.isalnum() or c.isspace() else "" for c in text)
    short = short.replace(" ", "_")
    
    # Kürze auf maximale Länge
    if len(short) > max_length:
        short = short[:max_length]
    
    return short.lower()


def format_text(text: str) -> list[str]:
    """
    Formatiert den Text in ein- oder zweizeilig.
    
    Args:
        text: Der zu formatierende Text
        
    Returns:
        Liste mit Textzeilen (1 oder 2 Zeilen)
    """
    # Wenn der Text kurz ist (< 30 Zeichen), eine Zeile
    if len(text) <= 30:
        return [text]
    
    # Versuche bei einem Leerzeichen in der Mitte zu trennen
    words = text.split()
    if len(words) <= 1:
        return [text]
    
    # Finde die optimale Trennstelle (möglichst in der Mitte)
    mid = len(text) // 2
    best_split = 0
    min_diff = float('inf')
    
    current_pos = 0
    for i, word in enumerate(words[:-1]):
        current_pos += len(word) + 1  # +1 für Leerzeichen
        diff = abs(current_pos - mid)
        if diff < min_diff:
            min_diff = diff
            best_split = i + 1
    
    line1 = " ".join(words[:best_split])
    line2 = " ".join(words[best_split:])
    
    return [line1, line2]


def add_watermark(image_path: str, text: str, opacity: int = 128, color: str = '#FFFFFF') -> Image.Image:
    """
    Fügt ein diagonales Wasserzeichen zu einem Bild hinzu.
    
    Args:
        image_path: Pfad zum Eingabebild
        text: Text für das Wasserzeichen
        opacity: Transparenz (0-255, wobei 128 = 50% transparent)
        color: Textfarbe als Hex-String (z.B. '#FFFFFF' für Weiß)
        
    Returns:
        PIL Image mit Wasserzeichen
    """
    # Öffne das Bild
    img = Image.open(image_path)
    
    # Konvertiere zu RGBA für Transparenz
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Konvertiere Hex-Farbe zu RGB
    color = color.lstrip('#')
    r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # Erstelle ein transparentes Overlay
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Formatiere den Text
    lines = format_text(text)
    
    # Berechne die Diagonale des Bildes (Zielbreite für das Wasserzeichen)
    diagonal = math.sqrt(img.width**2 + img.height**2)
    
    # Starte mit einer Basis-Schriftgröße
    base_font_size = min(img.size) // 20
    
    # Finde die längste Zeile
    longest_line = max(lines, key=len)
    
    # Lade die Schriftart und passe die Größe an, damit der Text die Diagonale ausfüllt
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    except:
        try:
            font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        except:
            font_path = None
    
    # Iterativ die optimale Schriftgröße finden
    # Ziel: Text soll ca. 80-90% der Diagonale ausfüllen
    target_width = diagonal * 0.85
    font_size = base_font_size
    
    # Binäre Suche für optimale Schriftgröße
    min_size = 10
    max_size = int(diagonal / len(longest_line)) * 3  # Obere Grenze basierend auf Textlänge
    
    for _ in range(15):  # Max 15 Iterationen
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
                break
        except:
            font = ImageFont.load_default()
            break
        
        # Messe die längste Zeile
        bbox = draw.textbbox((0, 0), longest_line, font=font)
        current_width = bbox[2] - bbox[0]
        
        # Wenn die Breite passt (±5%), fertig
        if abs(current_width - target_width) / target_width < 0.05:
            break
        
        # Passe Schriftgröße an
        if current_width < target_width:
            min_size = font_size
            font_size = (font_size + max_size) // 2
        else:
            max_size = font_size
            font_size = (min_size + font_size) // 2
        
        # Verhindere Endlosschleife
        if max_size - min_size <= 1:
            break
    
    # Finale Schriftart laden
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Berechne die Größe des Textes mit finaler Schrift
    line_spacing = font_size // 4
    total_height = 0
    max_width = 0
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        max_width = max(max_width, line_width)
        total_height += line_height
    
    if len(lines) > 1:
        total_height += line_spacing
    
    # Berechne den Winkel (diagonal)
    angle = math.degrees(math.atan2(img.height, img.width))
    
    # Erstelle ein temporäres Bild für den rotierten Text
    # Mache es groß genug für die Diagonale
    diagonal_int = int(diagonal)
    txt_img = Image.new('RGBA', (diagonal_int, diagonal_int), (255, 255, 255, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    
    # Zeichne den Text in der Mitte des temporären Bildes
    y_offset = (diagonal_int - total_height) // 2
    
    for i, line in enumerate(lines):
        bbox = txt_draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        
        x = (diagonal_int - line_width) // 2
        y = y_offset + i * (line_height + line_spacing)
        
        # Zeichne Text mit Transparenz
        txt_draw.text((x, y), line, font=font, fill=(r, g, b, opacity))
    
    # Rotiere das Text-Bild
    rotated = txt_img.rotate(angle, expand=False, resample=Image.BICUBIC)
    
    # Zentriere das rotierte Wasserzeichen auf dem Original
    paste_x = (img.width - diagonal_int) // 2
    paste_y = (img.height - diagonal_int) // 2
    
    # Füge das Wasserzeichen ein
    overlay.paste(rotated, (paste_x, paste_y), rotated)
    
    # Kombiniere Original und Overlay
    watermarked = Image.alpha_composite(img, overlay)
    
    return watermarked


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(
        description='Fügt ein diagonales Wasserzeichen zu einem Bild hinzu.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s bild.jpg "Mein Wasserzeichen"
  %(prog)s foto.png "Copyright 2025 Max Mustermann" --opacity 100
  %(prog)s bild.jpg "Vertraulich" --color "#FF0000" --opacity 180
        """
    )
    
    parser.add_argument(
        'image',
        type=str,
        help='Pfad zur Eingabe-Bilddatei'
    )
    
    parser.add_argument(
        'text',
        type=str,
        help='Text für das Wasserzeichen'
    )
    
    parser.add_argument(
        '--opacity',
        type=int,
        default=128,
        choices=range(0, 256),
        metavar='[0-255]',
        help='Transparenz des Wasserzeichens (0=unsichtbar, 255=undurchsichtig, Standard: 128)'
    )
    
    parser.add_argument(
        '--color',
        type=str,
        default='#FFFFFF',
        metavar='HEX',
        help='Textfarbe als Hex-Wert (z.B. #FFFFFF für Weiß, #FF0000 für Rot, Standard: #FFFFFF)'
    )
    
    args = parser.parse_args()
    
    # Prüfe ob Bilddatei existiert
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Fehler: Bilddatei '{args.image}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    
    if not image_path.is_file():
        print(f"Fehler: '{args.image}' ist keine Datei.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Erstelle Wasserzeichen
        print(f"Verarbeite Bild: {image_path.name}")
        watermarked_img = add_watermark(str(image_path), args.text, args.opacity, args.color)
        
        # Erstelle Ausgabedateinamen
        short_text = create_short_name(args.text)
        output_filename = f"{image_path.stem}-{short_text}.jpg"
        output_path = image_path.parent / output_filename
        
        # Konvertiere zu RGB für JPEG (falls RGBA)
        if watermarked_img.mode == 'RGBA':
            # Erstelle weißen Hintergrund
            rgb_img = Image.new('RGB', watermarked_img.size, (255, 255, 255))
            rgb_img.paste(watermarked_img, mask=watermarked_img.split()[3])  # 3 ist der Alpha-Kanal
            watermarked_img = rgb_img
        
        # Speichere das Bild
        watermarked_img.save(output_path, 'JPEG', quality=95)
        
        print(f"✓ Wasserzeichen hinzugefügt: {output_path.name}")
        print(f"  Speicherort: {output_path.absolute()}")
        
    except Exception as e:
        print(f"Fehler beim Verarbeiten des Bildes: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
