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

## Gestos
Reglas sobre los landmarks de MediaPipe (`src/gestures.py`). Los estáticos se mantienen ~0.4 s.

| Gesto | Evento |
|---|---|
| Puño | `PLAY_PAUSE` |
| Pellizco (pulgar + índice) | `SELECT` |
| Paz (índice + medio) | `MUTE_TOGGLE` |
| Mano abierta, movimiento horizontal rápido | `SWIPE_LEFT` / `SWIPE_RIGHT` |
| Mano abierta inclinada | `SEEK_BACKWARD` / `SEEK_FORWARD` |
| Pellizco sostenido hasta el borde de la imagen | `TRANSFER_LEFT` / `TRANSFER_RIGHT` |

Tests: `python -m unittest discover -s tests`

Diseño completo en `docs/DocumentoAnalisisDiseno-PDI.docx`.
