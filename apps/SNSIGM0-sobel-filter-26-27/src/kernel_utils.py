from enum import Enum
from math import floor

from safe_image import PixelChannels, SafeImage


class Direction(Enum):
    Vertical = 0
    Horizontal = 1


def offset_pos(pos: (int, int), offset: int, direction: Direction) -> (int, int):
    match (direction):
        case Direction.Vertical:
            return (pos[0], pos[1] + offset)
        case Direction.Horizontal:
            return (pos[0] + offset, pos[1])
        case _:
            return pos


def is_pos_in_image(image: SafeImage, pos: (int, int)) -> bool:
    width: int = image.get_image().width
    height: int = image.get_image().height
    x: int = pos[0]
    y: int = pos[1]
    return (x >= 0 and x < width) and (y >= 0 and y < height)


def sample_kernel(
    image: SafeImage, pos: (int, int), kernel: list[float], direction: Direction
) -> list[float]:
    result: list[float] = []
    kernel_size = len(kernel)
    half_size = floor(kernel_size / 2)
    for index in range(kernel_size):
        weight: float = kernel[index]
        offset: int = index - half_size
        sample_pos = offset_pos(pos, offset, direction)
        if not is_pos_in_image(image, sample_pos):
            continue

        result.append(
            PixelChannels(image.get_image().getpixel(sample_pos)).get_first() * weight
        )

    return result


def mean(samples: list[float]) -> float:
    size: int = len(samples)
    mean: float = 0
    for sample in samples:
        mean += sample

    return mean / size


def convolve_1d(
    grid: list[list[float]],
    kernel: list[int],
    direction: Direction,
    on_row=None,
) -> list[list[float]]:
    """Applique un noyau 1D sur une grille de flottants grid[y][x].

    Somme ponderee (pas de moyenne), aucune troncature ni clamp :
    les valeurs negatives sont conservees. Aux bords, on repete le
    pixel le plus proche.
    """
    height, width = len(grid), len(grid[0])
    half = len(kernel) // 2
    out: list[list[float]] = [[0.0] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            acc = 0.0
            for index, weight in enumerate(kernel):
                sx, sy = offset_pos((x, y), index - half, direction)
                sx = min(max(sx, 0), width - 1)
                sy = min(max(sy, 0), height - 1)
                acc += grid[sy][sx] * weight
            out[y][x] = acc
        if on_row is not None:
            on_row()
    return out
