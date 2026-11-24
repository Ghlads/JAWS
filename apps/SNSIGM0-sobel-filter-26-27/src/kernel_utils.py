from enum import Enum

# Image en niveaux de gris : grid[y][x], valeurs flottantes (0..255 en entree,
# mais les calculs intermediaires peuvent sortir de cet intervalle).
Grid = list[list[float]]


class Direction(Enum):
    Vertical = 0
    Horizontal = 1


def convolve_1d(
    grid: Grid,
    kernel: list[float],
    direction: Direction,
    on_row=None,
) -> Grid:
    """Applique un noyau 1D sur une grille de flottants grid[y][x].

    Somme ponderee (pas de moyenne), aucune troncature ni clamp :
    les valeurs negatives sont conservees. Aux bords, on repete le
    pixel le plus proche.

    Au lieu de boucler pixel par pixel, on additionne des lignes entieres
    decalees (une par coefficient du noyau) : beaucoup moins d'operations
    Python par pixel.
    """
    height, width = len(grid), len(grid[0])
    half = len(kernel) // 2
    # (decalage, poids) en ignorant les coefficients nuls
    taps = [(i - half, float(w)) for i, w in enumerate(kernel) if w != 0]

    out: Grid = []
    for y in range(height):
        acc = [0.0] * width
        if direction is Direction.Horizontal:
            row = grid[y]
            padded = [row[0]] * half + row + [row[-1]] * half
            for offset, weight in taps:
                start = offset + half
                acc = [a + weight * s for a, s in zip(acc, padded[start : start + width])]
        else:
            for offset, weight in taps:
                src = grid[min(max(y + offset, 0), height - 1)]
                acc = [a + weight * s for a, s in zip(acc, src)]
        out.append(acc)
        if on_row is not None:
            on_row()
    return out
