#!/usr/bin/env python3
"""
Flask Web-App für Wasserzeichen
"""

from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'uploads'

# Erstelle Upload-Ordner falls nicht vorhanden
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}


def allowed_file(filename):
    """Prüfe ob Dateiendung erlaubt ist"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def format_text(text: str) -> list[str]:
    """Formatiert den Text in ein- oder zweizeilig"""
    if len(text) <= 30:
        return [text]
    
    words = text.split()
    if len(words) <= 1:
        return [text]
    
    mid = len(text) // 2
    best_split = 0
    min_diff = float('inf')
    
    current_pos = 0
    for i, word in enumerate(words[:-1]):
        current_pos += len(word) + 1
        diff = abs(current_pos - mid)
        if diff < min_diff:
            min_diff = diff
            best_split = i + 1
    
    line1 = " ".join(words[:best_split])
    line2 = " ".join(words[best_split:])
    
    return [line1, line2]


def add_watermark(img: Image.Image, text: str, opacity: int = 128, color: str = '#FFFFFF') -> Image.Image:
    """Fügt ein diagonales Wasserzeichen zu einem Bild hinzu"""
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
    
    # Berechne die Diagonale des Bildes
    diagonal = math.sqrt(img.width**2 + img.height**2)
    
    # Starte mit einer Basis-Schriftgröße
    base_font_size = min(img.size) // 20
    
    # Finde die längste Zeile
    longest_line = max(lines, key=len)
    
    # Lade die Schriftart
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    except:
        try:
            font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        except:
            font_path = None
    
    # Iterativ die optimale Schriftgröße finden
    target_width = diagonal * 0.85
    font_size = base_font_size
    
    min_size = 10
    max_size = int(diagonal / len(longest_line)) * 3
    
    for _ in range(15):
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
                break
        except:
            font = ImageFont.load_default()
            break
        
        bbox = draw.textbbox((0, 0), longest_line, font=font)
        current_width = bbox[2] - bbox[0]
        
        if abs(current_width - target_width) / target_width < 0.05:
            break
        
        if current_width < target_width:
            min_size = font_size
            font_size = (font_size + max_size) // 2
        else:
            max_size = font_size
            font_size = (min_size + font_size) // 2
        
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
    
    # Berechne die Größe des Textes
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
    diagonal_int = int(diagonal)
    txt_img = Image.new('RGBA', (diagonal_int, diagonal_int), (255, 255, 255, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    
    # Zeichne den Text
    y_offset = (diagonal_int - total_height) // 2
    
    for i, line in enumerate(lines):
        bbox = txt_draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        
        x = (diagonal_int - line_width) // 2
        y = y_offset + i * (line_height + line_spacing)
        
        txt_draw.text((x, y), line, font=font, fill=(r, g, b, opacity))
    
    # Rotiere das Text-Bild
    rotated = txt_img.rotate(angle, expand=False, resample=Image.BICUBIC)
    
    # Zentriere das rotierte Wasserzeichen
    paste_x = (img.width - diagonal_int) // 2
    paste_y = (img.height - diagonal_int) // 2
    
    overlay.paste(rotated, (paste_x, paste_y), rotated)
    
    # Kombiniere Original und Overlay
    watermarked = Image.alpha_composite(img, overlay)
    
    return watermarked


@app.route('/')
def index():
    """Hauptseite"""
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_image():
    """Verarbeite das Bild mit Wasserzeichen"""
    if 'image' not in request.files:
        return jsonify({'error': 'Kein Bild hochgeladen'}), 400
    
    file = request.files['image']
    text = request.form.get('text', '')
    opacity = int(request.form.get('opacity', 128))
    color = request.form.get('color', '#FFFFFF')
    
    if not text:
        return jsonify({'error': 'Kein Text angegeben'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Ungültiges Dateiformat'}), 400
    
    try:
        # Öffne das Bild
        img = Image.open(file.stream)
        
        # Füge Wasserzeichen hinzu
        watermarked = add_watermark(img, text, opacity, color)
        
        # Konvertiere zu RGB für JPEG
        if watermarked.mode == 'RGBA':
            rgb_img = Image.new('RGB', watermarked.size, (255, 255, 255))
            rgb_img.paste(watermarked, mask=watermarked.split()[3])
            watermarked = rgb_img
        
        # Speichere in BytesIO
        img_io = io.BytesIO()
        watermarked.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        # Konvertiere zu Base64 für Anzeige
        img_base64 = base64.b64encode(img_io.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_base64}'
        })
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Verarbeiten: {str(e)}'}), 500


@app.route('/download', methods=['POST'])
def download_image():
    """Download des Bildes mit Wasserzeichen"""
    try:
        # Hole Base64-kodiertes Bild aus Request
        image_data = request.json.get('image', '')
        
        if not image_data.startswith('data:image/jpeg;base64,'):
            return jsonify({'error': 'Ungültige Bilddaten'}), 400
        
        # Dekodiere Base64
        img_data = base64.b64decode(image_data.split(',')[1])
        
        # Erstelle BytesIO
        img_io = io.BytesIO(img_data)
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='watermarked.jpg'
        )
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Download: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
