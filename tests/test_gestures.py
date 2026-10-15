import math
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import gestures as g  # noqa: E402

# (side, radio) de mcp, pip, dip, tip para un dedo extendido / doblado
FINGER_SIDE = {"index": -0.03, "middle": 0.0, "ring": 0.03, "pinky": 0.06}
EXTENDED = (0.20, 0.30, 0.37, 0.43)
FOLDED = (0.20, 0.28, 0.24, 0.18)


def make_hand(fingers=(), thumb=False, pinch=False, cx=0.5, cy=0.7, angle=0.0):
    """Mano sintética. `fingers`: nombres de dedos extendidos. angle: grados, + = a la derecha."""
    a = math.radians(angle)
    up = (math.sin(a), -math.cos(a))
    side = (math.cos(a), math.sin(a))

    def pt(s, r):
        return SimpleNamespace(x=cx + side[0] * s + up[0] * r, y=cy + side[1] * s + up[1] * r)

    lm = [None] * 21
    lm[0] = pt(0, 0)
    thumb_pts = [(-0.05, 0.05), (-0.09, 0.12), (-0.14, 0.17), (-0.19, 0.21)] if thumb else [
        (-0.05, 0.05), (-0.06, 0.10), (-0.06, 0.12), (0.0, 0.14)]
    for i, (s, r) in enumerate(thumb_pts):
        lm[1 + i] = pt(s, r)
    for name, base in (("index", 5), ("middle", 9), ("ring", 13), ("pinky", 17)):
        shape = EXTENDED if name in fingers else FOLDED
        for i, r in enumerate(shape):
            lm[base + i] = pt(FINGER_SIDE[name], r)
    if pinch:
        lm[4] = SimpleNamespace(x=lm[8].x, y=lm[8].y)
    return lm


def run(rec, frames):
    """frames: lista de (mano, t). Devuelve todos los eventos emitidos."""
    out = []
    for lm, t in frames:
        out += rec.update(lm, t)[1]
    return out


ALL = ("index", "middle", "ring", "pinky")


class PoseTests(unittest.TestCase):
    def test_poses(self):
        self.assertEqual(g.classify_pose(make_hand(ALL, thumb=True)), "OPEN")
        self.assertEqual(g.classify_pose(make_hand()), "FIST")
        self.assertEqual(g.classify_pose(make_hand(("index",), pinch=True)), "PINCH")
        self.assertEqual(g.classify_pose(make_hand(("index",))), "NONE")

    def test_pose_rotation_invariant(self):
        self.assertEqual(g.classify_pose(make_hand(ALL, thumb=True, angle=60)), "OPEN")
        self.assertEqual(g.classify_pose(make_hand(angle=-60)), "FIST")


class EventTests(unittest.TestCase):
    def test_fist_needs_hold(self):
        rec = g.GestureRecognizer()
        fist = make_hand()
        self.assertEqual(run(rec, [(fist, 0.0), (fist, 0.2)]), [])
        self.assertEqual(run(rec, [(fist, 0.5)]), ["FIST"])
        self.assertEqual(run(rec, [(fist, 0.9)]), [])  # una sola vez por gesto

    def test_pinch_is_fast(self):
        rec = g.GestureRecognizer()
        pinch = make_hand(("index",), pinch=True)
        self.assertEqual(run(rec, [(pinch, 0.0), (pinch, 0.1)]), [])
        self.assertEqual(run(rec, [(pinch, 0.2), (pinch, 0.6)]), ["PINCH"])

    def test_removed_gestures_do_nothing(self):
        rec = g.GestureRecognizer()
        peace = make_hand(("index", "middle"))
        tilted = make_hand(ALL, thumb=True, angle=50)
        self.assertEqual(run(rec, [(peace, i * 0.2) for i in range(6)]), [])
        self.assertEqual(run(rec, [(tilted, 2 + i * 0.2) for i in range(6)]), [])

    def test_swipe(self):
        for sign, name in ((1, "SWIPE_RIGHT"), (-1, "SWIPE_LEFT")):
            rec = g.GestureRecognizer()
            frames = [(make_hand(ALL, thumb=True, cx=0.5 + sign * 0.06 * i), i * 0.05) for i in range(8)]
            self.assertEqual(run(rec, frames), [name])

    def test_slow_motion_is_not_swipe(self):
        rec = g.GestureRecognizer()
        frames = [(make_hand(ALL, thumb=True, cx=0.3 + 0.004 * i), i * 0.05) for i in range(40)]
        self.assertEqual(run(rec, frames), [])

    def test_upright_open_hand_does_nothing(self):
        rec = g.GestureRecognizer()
        self.assertEqual(run(rec, [(make_hand(ALL, thumb=True), i * 0.1) for i in range(20)]), [])

    def test_no_hand_resets(self):
        rec = g.GestureRecognizer()
        fist = make_hand()
        run(rec, [(fist, 0.0)])
        self.assertEqual(rec.update(None, 0.3), ("NONE", []))
        self.assertEqual(run(rec, [(fist, 0.4), (fist, 0.6)]), [])  # el conteo de hold reinicia


class PointerTests(unittest.TestCase):
    def test_map_to_screen(self):
        from controller import ACTIVE_X, ACTIVE_Y, map_to_screen
        self.assertEqual(map_to_screen(ACTIVE_X[0], ACTIVE_Y[0], 1000, 800), (0, 0))
        self.assertEqual(map_to_screen(ACTIVE_X[1], ACTIVE_Y[1], 1000, 800), (999, 799))
        self.assertEqual(map_to_screen(0.0, 1.0, 1000, 800), (0, 799))  # fuera de la zona: se limita
        mx, my = map_to_screen(0.5, (ACTIVE_Y[0] + ACTIVE_Y[1]) / 2, 1000, 800)
        self.assertAlmostEqual(mx, 499.5)

    def test_actions(self):
        from controller import ACTIONS
        self.assertEqual(ACTIONS["FIST"], ("key", "m"))
        self.assertEqual(ACTIONS["PINCH"][0], "left_click")
        self.assertEqual(ACTIONS["SWIPE_LEFT"], ("key", "left"))
        self.assertEqual(ACTIONS["SWIPE_RIGHT"], ("key", "right"))


if __name__ == "__main__":
    unittest.main()
