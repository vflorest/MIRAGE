# MIRAGE
MIRAGE — Multiplatform Image Recognition And Gesture Experience. Sistema de manipulación de imágenes entre dispositivos mediante reconocimiento de gestos.

## Funcionalidades
- Seleccionar imágenes
- Arrastrar y mover dentro del dispositivo
- Transferir imágenes entre dispositivos según orientación
- Eliminar imágenes con confirmación gestual
- Navegar en galería con barridos izquierda/derecha

## Tecnologías candidatas
- Python 3.10+
- OpenCV, MediaPipe
- PyTorch/ONNX
- WebSockets/WebRTC

## Instalación (sin Docker)
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```
En macOS, la primera ejecución pedirá permiso de cámara para la terminal.
