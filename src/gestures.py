"""Reconocimiento de gestos por reglas sobre los 21 landmarks de MediaPipe.

Gestos estáticos (se mantienen ~HOLD_S segundos para activarse):
    PINCH  (pulgar + índice juntos)  -> SELECT
    FIST   (puño cerrado)            -> PLAY_PAUSE
    PEACE  (índice + medio, en V)    -> MUTE_TOGGLE

Gestos dinámicos con la mano abierta (OPEN):
    movimiento horizontal rápido     -> SWIPE_LEFT / SWIPE_RIGHT
    inclinar (girar) la mano         -> SEEK_BACKWARD / SEEK_FORWARD (se repite)

Arrastre:
    PINCH sostenido hasta el borde   -> TRANSFER_LEFT / TRANSFER_RIGHT

Las direcciones se expresan en la imagen espejada (la que ve el usuario).
"""

import math
from collections import deque

WRIST = 0
THUMB_IP, THUMB_TIP = 3, 4
INDEX_MCP, INDEX_TIP = 5, 8
MIDDLE_MCP = 9
PINKY_MCP = 17
# (pip, tip) de índice, medio, anular y meñique
FINGERS = {"index": (6, 8), "middle": (10, 12), "ring": (14, 16), "pinky": (18, 20)}

PINCH_RATIO = 0.3  # distancia pulgar-índice / tamaño de la mano
PINCH_MIN_INDEX_REACH = 1.1  # alcance muñeca-punta del índice / tamaño de la mano
HOLD_S = 0.4  # tiempo para activar un gesto estático
SWIPE_WINDOW_S = 0.4
SWIPE_MIN_DX = 0.30  # fracción del ancho de la imagen
SWIPE_COOLDOWN_S = 1.0
SEEK_ANGLE_DEG = 35
SEEK_REPEAT_S = 0.5
TRANSFER_EDGE = 0.08  # margen del borde, fracción del ancho


def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def hand_size(lm):
    return _dist(lm[WRIST], lm[MIDDLE_MCP]) or 1e-6


def finger_states(lm):
    """Dedos extendidos, independiente de la rotación de la mano."""
    wrist = lm[WRIST]
    states = {
        name: _dist(lm[tip], wrist) > _dist(lm[pip], wrist) * 1.1
        for name, (pip, tip) in FINGERS.items()
    }
    states["thumb"] = _dist(lm[THUMB_TIP], lm[PINKY_MCP]) > _dist(lm[THUMB_IP], lm[PINKY_MCP]) * 1.05
    return states


def is_pinch(lm):
    size = hand_size(lm)
    close = _dist(lm[THUMB_TIP], lm[INDEX_TIP]) / size < PINCH_RATIO
    # en un puño el pulgar también toca el índice, pero el índice está recogido
    index_raised = _dist(lm[INDEX_TIP], lm[WRIST]) / size > PINCH_MIN_INDEX_REACH
    return close and index_raised


def classify_pose(lm):
    if is_pinch(lm):
        return "PINCH"
    f = finger_states(lm)
    four = [f["index"], f["middle"], f["ring"], f["pinky"]]
    if all(four) and f["thumb"]:
        return "OPEN"
    if not any(four):
        return "FIST"
    if f["index"] and f["middle"] and not f["ring"] and not f["pinky"]:
        return "PEACE"
    return "NONE"


def palm_center(lm):
    return lm[WRIST].x * 0.5 + lm[MIDDLE_MCP].x * 0.5, lm[WRIST].y * 0.5 + lm[MIDDLE_MCP].y * 0.5


def roll_angle(lm):
    """Inclinación de la mano respecto a la vertical, en grados (+ = hacia la derecha)."""
    dx = lm[MIDDLE_MCP].x - lm[WRIST].x
    dy = lm[MIDDLE_MCP].y - lm[WRIST].y
    return math.degrees(math.atan2(dx, -dy))


STATIC_EVENTS = {"PINCH": "SELECT", "FIST": "PLAY_PAUSE", "PEACE": "MUTE_TOGGLE"}


class GestureRecognizer:
    """Procesa una mano por fotograma y devuelve (pose, eventos)."""

    def __init__(self):
        self.reset()

    def reset(self):
        self._pose = "NONE"
        self._pose_since = 0.0
        self._pose_fired = False
        self._xs = deque()  # (t, x) del centro de la palma con la mano abierta
        self._swipe_ready_at = 0.0
        self._next_seek_at = 0.0
        self._transfer_fired = False

    def update(self, lm, t):
        """lm: lista de 21 landmarks normalizados, o None si no hay mano. t en segundos."""
        if lm is None:
            self.reset()
            return "NONE", []

        events = []
        pose = classify_pose(lm)
        cx, _ = palm_center(lm)

        if pose != self._pose:
            self._pose, self._pose_since, self._pose_fired = pose, t, False
            self._transfer_fired = False
            self._xs.clear()

        if pose in STATIC_EVENTS and not self._pose_fired and t - self._pose_since >= HOLD_S:
            events.append(STATIC_EVENTS[pose])
            self._pose_fired = True

        if pose == "PINCH" and not self._transfer_fired:
            if cx < TRANSFER_EDGE:
                events.append("TRANSFER_LEFT")
                self._transfer_fired = True
            elif cx > 1 - TRANSFER_EDGE:
                events.append("TRANSFER_RIGHT")
                self._transfer_fired = True

        if pose == "OPEN":
            self._xs.append((t, cx))
            while self._xs and t - self._xs[0][0] > SWIPE_WINDOW_S:
                self._xs.popleft()
            dx = cx - self._xs[0][1]
            if abs(dx) >= SWIPE_MIN_DX and t >= self._swipe_ready_at:
                events.append("SWIPE_RIGHT" if dx > 0 else "SWIPE_LEFT")
                self._swipe_ready_at = t + SWIPE_COOLDOWN_S
                self._xs.clear()

            angle = roll_angle(lm)
            if abs(angle) >= SEEK_ANGLE_DEG and t >= self._next_seek_at:
                events.append("SEEK_FORWARD" if angle > 0 else "SEEK_BACKWARD")
                self._next_seek_at = t + SEEK_REPEAT_S

        return pose, events
