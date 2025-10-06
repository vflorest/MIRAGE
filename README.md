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

# ===============================
# MIRAGE Webcam + Docker (Mac/Win)
# ===============================

# 1️⃣  Configura el display para XQuartz/VcXsrv
x11-setup:
	@echo "🎨 Configurando servidor gráfico..."
	@if [ "$$(uname)" = "Darwin" ]; then \
		open -a XQuartz; \
		sleep 2; \
		export IP=$$(ifconfig en0 | grep inet | awk '$$1=="inet" {print $$2}'); \
		xhost + $$IP; \
		echo "✅ XQuartz configurado con IP $$IP"; \
	else \
		echo "🪟 En Windows usa VcXsrv (con 'Disable access control') y socat"; \
	fi

# 2️⃣  Abre el túnel entre XQuartz/VcXsrv y Docker
x11-forward:
	@echo "🔄 Creando puente con socat..."
	@if [ "$$(uname)" = "Darwin" ]; then \
		socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$$DISPLAY\" & \
	else \
		echo "Usa socat o WSL con: socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$$DISPLAY\" &"; \
	fi

# 3️⃣  Ejecuta MIRAGE en Docker con acceso a cámara
run-docker:
	@echo "🚀 Iniciando MIRAGE en Docker con cámara..."
	docker-compose up --build

# 4️⃣  Apagar contenedor
down:
	docker-compose down

