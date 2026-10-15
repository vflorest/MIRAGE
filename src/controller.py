"""Traduce eventos de gestos en acciones del sistema y mueve el puntero con la mano."""

import pyautogui

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False  # el puntero llega a las esquinas a propósito

ACTIONS = {
    "FIST": ("key", "m"),
    "PINCH": ("right_click", None),
    "SWIPE_LEFT": ("key", "left"),
    "SWIPE_RIGHT": ("key", "right"),
}

# Zona central de la imagen que cubre toda la pantalla, para llegar a los bordes
# sin tener que sacar la mano del encuadre.
ACTIVE_X = (0.2, 0.8)
ACTIVE_Y = (0.15, 0.7)
SMOOTHING = 0.35  # 0 = congelado, 1 = sin suavizado


def map_to_screen(x, y, screen_w, screen_h):
    """Coordenadas normalizadas de la imagen -> píxeles de pantalla (limitado a la pantalla)."""
    nx = (x - ACTIVE_X[0]) / (ACTIVE_X[1] - ACTIVE_X[0])
    ny = (y - ACTIVE_Y[0]) / (ACTIVE_Y[1] - ACTIVE_Y[0])
    nx = min(max(nx, 0.0), 1.0)
    ny = min(max(ny, 0.0), 1.0)
    return nx * (screen_w - 1), ny * (screen_h - 1)


class Controller:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.screen_w, self.screen_h = pyautogui.size()
        self._pos = None

    def move_pointer(self, x, y):
        """Mueve el puntero a la posición normalizada (x, y) con suavizado. Devuelve (px, py)."""
        tx, ty = map_to_screen(x, y, self.screen_w, self.screen_h)
        if self._pos is None:
            self._pos = (tx, ty)
        else:
            px, py = self._pos
            self._pos = (px + (tx - px) * SMOOTHING, py + (ty - py) * SMOOTHING)
        if self.enabled:
            pyautogui.moveTo(*self._pos)
        return self._pos

    def lost_hand(self):
        self._pos = None

    def handle(self, event):
        action, arg = ACTIONS[event]
        if not self.enabled:
            return
        if action == "key":
            pyautogui.press(arg)
        elif action == "right_click":
            pyautogui.click(button="right")
