from pathlib import Path
from safe_image import SafeImage
from PIL import Image

def load_image(path: Path) -> SafeImage:
    return SafeImage(path)

def save_image(safe_image: SafeImage, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_image.get_image().save(path)
