from PIL import Image
from pathlib import Path

class SafeImage:
    def __init__(self, image_path: Path):
        self.image = Image.open(image_path)

    def get_image(self) -> Image.Image:
        return self.image

    def release(self) -> None:
        if self.image:
            self.image.close()
            self.image = None

    def is_released(self) -> bool:
        return self.image is None

    def __del__(self):
        if not self.is_released():
            self.release()
            print("Warning: Image resource was not released before object deletion. Resource has been released automatically.")