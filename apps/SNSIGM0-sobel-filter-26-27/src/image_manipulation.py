from pathlib import Path

from safe_image import SafeImage


def load_image(path: Path) -> SafeImage:
    return SafeImage(path.name).FromPath(path)


def save_image(safe_image: SafeImage, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_image.get_image().save(path)


def _lerp(a: float, b: float, t: float) -> float:
    return (1.0 - t) * a + t * b


def _inverse_lerp(a: float, b: float, v: float) -> float:
    return (v - a) / (b - a)


def _remap(
    value: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    return _lerp(out_min, out_max, _inverse_lerp(in_min, in_max, value))


def remap_pixel_to_float(pixel: int) -> float:
    return _remap(float(pixel), 0.0, 255.0, 0.0, 1.0)


def remap_pixel_to_int(pixel: float) -> int:
    return int(_remap(pixel, 0.0, 1.0, 0.0, 255.0))
