from pathlib import Path

from PIL import Image

from kernel_utils import Grid


def load_image(path: Path) -> Grid:
    """Charge une image et la convertit en niveaux de gris (grid[y][x]).

    convert("L") utilise la formule de luminance L = 0.299 R + 0.587 G + 0.114 B.
    PIL n'est utilise qu'ici et dans save_image.
    """
    with Image.open(path) as img:
        gray = img.convert("L")
        width, height = gray.size
        raw = gray.tobytes()
    return [
        [float(v) for v in raw[y * width : (y + 1) * width]] for y in range(height)
    ]


def save_image(grid: Grid, path: Path) -> None:
    """Ecrit une grille en image niveaux de gris, valeurs ramenees dans 0..255."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    height, width = len(grid), len(grid[0])
    data = bytes(min(255, max(0, int(v))) for row in grid for v in row)
    Image.frombytes("L", (width, height), data).save(path)
