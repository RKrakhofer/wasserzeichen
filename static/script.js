// Globale Variablen
let selectedFile = null;
let processedImageData = null;

// DOM Elemente
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const watermarkText = document.getElementById('watermarkText');
const opacitySlider = document.getElementById('opacity');
const opacityValue = document.getElementById('opacityValue');
const colorInput = document.getElementById('color');
const colorValue = document.getElementById('colorValue');
const processBtn = document.getElementById('processBtn');
const downloadBtn = document.getElementById('downloadBtn');
const previewContainer = document.getElementById('previewContainer');
const originalPreview = document.getElementById('originalPreview');
const previewImage = document.getElementById('previewImage');
const originalImage = document.getElementById('originalImage');
const loading = document.getElementById('loading');
const errorDiv = document.getElementById('error');

// Event Listeners
dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', handleDragOver);
dropzone.addEventListener('dragleave', handleDragLeave);
dropzone.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
watermarkText.addEventListener('input', updateButtonState);
opacitySlider.addEventListener('input', updateOpacityDisplay);
colorInput.addEventListener('input', updateColorDisplay);
processBtn.addEventListener('click', processImage);
downloadBtn.addEventListener('click', downloadImage);

// Funktionen
function handleDragOver(e) {
    e.preventDefault();
    dropzone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropzone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // Prüfe ob es ein Bild ist
    if (!file.type.startsWith('image/')) {
        showError('Bitte wählen Sie eine Bilddatei aus.');
        return;
    }
    
    selectedFile = file;
    
    // Zeige Vorschau des Originals
    const reader = new FileReader();
    reader.onload = (e) => {
        originalImage.src = e.target.result;
        originalPreview.style.display = 'block';
        dropzone.classList.add('has-file');
    };
    reader.readAsDataURL(file);
    
    // Verstecke altes Ergebnis
    previewContainer.style.display = 'none';
    hideError();
    
    updateButtonState();
}

function updateOpacityDisplay() {
    const value = opacitySlider.value;
    const percent = Math.round((value / 255) * 100);
    opacityValue.textContent = `${percent}%`;
}

function updateColorDisplay() {
    colorValue.textContent = colorInput.value.toUpperCase();
}

function updateButtonState() {
    processBtn.disabled = !(selectedFile && watermarkText.value.trim());
}

function showLoading() {
    loading.style.display = 'flex';
}

function hideLoading() {
    loading.style.display = 'none';
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    errorDiv.style.display = 'none';
}

async function processImage() {
    if (!selectedFile || !watermarkText.value.trim()) {
        return;
    }
    
    showLoading();
    hideError();
    
    // Erstelle FormData
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('text', watermarkText.value.trim());
    formData.append('opacity', opacitySlider.value);
    formData.append('color', colorInput.value);
    
    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Verarbeiten');
        }
        
        // Zeige Vorschau
        processedImageData = data.image;
        previewImage.src = data.image;
        previewContainer.style.display = 'block';
        
        // Scroll zur Vorschau
        previewContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

async function downloadImage() {
    if (!processedImageData) {
        return;
    }
    
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: processedImageData
            })
        });
        
        if (!response.ok) {
            throw new Error('Fehler beim Download');
        }
        
        // Erstelle Blob und Download-Link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // Erstelle Dateinamen
        const text = watermarkText.value.trim();
        const shortText = text.replace(/[^a-zA-Z0-9\s]/g, '').replace(/\s+/g, '_').toLowerCase().substring(0, 20);
        a.download = `watermarked-${shortText || 'image'}.jpg`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        showError('Fehler beim Download: ' + error.message);
    }
}

// Initialisierung
updateOpacityDisplay();
updateColorDisplay();
