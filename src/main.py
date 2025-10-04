import cv2
import mediapipe as mp

print("✅ MIRAGE iniciado correctamente")

# Test de cámara
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("⚠️ No se detecta cámara")
else:
    print("🎥 Cámara detectada correctamente")
    cap.release()
