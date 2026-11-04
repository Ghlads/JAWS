from pathlib import Path
import numpy as np
from PIL import Image

def load_image(path: Path) -> np.ndarray:
    with Image.open(path) as img:
        return np.array(img, dtype=np.float64)

def save_image(array: np.ndarray, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(array, 0, 255).astype(np.uint8)).save(path)
