from pathlib import Path

from PIL import Image


class PixelChannels:
    def __init__(self, channel_values: tuple[int, ...]):
        self.raw = channel_values

    def get_first(self) -> int:
        return self.raw[0]

    def has_rgb(self) -> bool:
        return len(self.raw) >= 3

    def has_alpha(self) -> bool:
        return len(self.raw) == 4 or len(self.raw) == 2

    def get_rgb(self) -> tuple[int, int, int]:
        if not self.has_rgb():
            raise ValueError("Pixel does not have RGB channels.")
        return self.raw[0], self.raw[1], self.raw[2]

    def get_alpha(self) -> int:
        if not self.has_alpha():
            raise ValueError("Pixel does not have an alpha channel.")
        return self.raw[-1]

    def set_rgb(self, r: int, g: int, b: int) -> None:
        if not self.has_rgb():
            raise ValueError("Pixel does not have RGB channels.")
        self.raw = (r, g, b) + self.raw[3:]

    def set_alpha(self, alpha: int) -> None:
        if not self.has_alpha():
            raise ValueError("Pixel does not have an alpha channel.")
        self.raw = self.raw[:-1] + (alpha,)


class SafeImage:
    def __init__(self, name: str = "noname"):
        self.name = name
        self.is_locked = False

    def FromPath(self, image_path: Path) -> "SafeImage":
        self.image = Image.open(image_path)
        return self

    def FromImage(self, image: Image.Image) -> "SafeImage":
        self.image = image
        if self.image is None:
            raise ValueError("Image cannot be None.")
        self.image.load()
        return self

    def get_image(self) -> Image.Image:
        return self.image

    def lock(self) -> None:
        self.is_locked = True

    def unlock(self) -> None:
        self.is_locked = False

    def release(self) -> None:
        if self.image and not self.is_locked:
            self.image.close()
            self.image = None

    def is_released(self) -> bool:
        return self.image is None

    def Copy(self, name_override: [str, None] = None) -> "SafeImage":
        if self.is_released():
            raise ValueError("Cannot copy a released image.")
        name = self.name + "_copy" if name_override is None else name_override
        return SafeImage(name).FromImage(self.image.copy())

    def __del__(self):
        if not self.is_released():
            self.release()
            print(
                "Warning: Image {name} resource was not released before object deletion. Resource has been released automatically.".format(
                    name=self.name
                )
            )
