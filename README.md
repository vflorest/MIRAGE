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
Reglas sobre los landmarks de MediaPipe (`src/gestures.py`) y acciones en `src/controller.py`.
El puntero del sistema sigue el centro de la palma.

| Gesto | Acción |
|---|---|
| Puño (~0.4 s) | tecla `m` |
| Pellizco (pulgar + índice) | clic derecho |
| Mano abierta, barrido rápido a la izquierda | tecla `←` |
| Mano abierta, barrido rápido a la derecha | tecla `→` |

Ventana: `q` sale, `c` activa/desactiva el control del sistema. `python src/main.py --dry-run` arranca sin controlar el sistema.
En macOS hay que dar permiso de Accesibilidad a la terminal (Ajustes > Privacidad y seguridad) para que se muevan el puntero y las teclas.

Tests: `python -m unittest discover -s tests`

Diseño completo en `docs/DocumentoAnalisisDiseno-PDI.docx`.
