import itertools
import sys
import time

_FRAMES = itertools.cycle("-\\|/")
_INTERVAL = 0.1  # secondes entre deux redessins
_WIDTH = 70  # largeur max de la ligne (efface les restes)

_label = ""
_last_draw = 0.0


def _draw():
    text = f"{next(_FRAMES)} {_label}"
    sys.stdout.write("\r" + text.ljust(_WIDTH))
    sys.stdout.flush()


def set_label(label: str) -> None:
    global _label, _last_draw
    _label = label
    _last_draw = time.monotonic()
    _draw()


def update() -> None:
    global _last_draw
    now = time.monotonic()
    if now - _last_draw < _INTERVAL:
        return
    _last_draw = now
    _draw()


def done(message: str = "Terminé") -> None:
    sys.stdout.write("\r" + f"✓ {message}".ljust(_WIDTH) + "\n")
    sys.stdout.flush()
