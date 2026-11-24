from math import hypot
from random import gauss, random

from kernel_utils import Direction, Grid, convolve_1d
from throttler import set_label, update


class Filter:
    """Un filtre prend une grille et renvoie une NOUVELLE grille.

    La grille d'entree n'est jamais modifiee : on peut donc reutiliser la
    meme source pour plusieurs filtres sans copie ni verrou.
    """

    def __init__(self, filter_name: str):
        self.name = filter_name

    def apply(self, grid: Grid, label: str = "") -> Grid:
        set_label(f"{self.name} : {label}")
        return self.process(grid)

    def process(self, grid: Grid) -> Grid:
        raise NotImplementedError


class PixelFilter(Filter):
    """Filtre ou chaque pixel ne depend que de sa propre valeur."""

    def process(self, grid: Grid) -> Grid:
        out: Grid = []
        compute = self.compute
        for row in grid:
            out.append([compute(v) for v in row])
            update()
        return out

    def compute(self, value: float) -> float:
        return value


class KernelFilter(Filter):
    """Filtre de contours separable : G = scalar * (lissage ⊗ derivee).

    Les calculs intermediaires sont faits en flottants pour garder les
    valeurs negatives et superieures a 255 ; on ne revient en 8 bits
    qu'a la sauvegarde.

    Si `threshold` n'est pas None, la magnitude est seuillee :
    255 si magnitude >= threshold, sinon 0.
    """

    def __init__(
        self,
        smooth_kernel: list[float],
        derivation_kernel: list[float],
        scalar: float,
        threshold: float | None,
        filter_name: str,
    ):
        super().__init__(filter_name)
        self.smooth = smooth_kernel
        self.deriv = derivation_kernel
        self.scalar = scalar
        self.threshold = threshold

    def process(self, grid: Grid) -> Grid:
        # Gx : lissage vertical puis derivee horizontale
        gx = convolve_1d(
            convolve_1d(grid, self.smooth, Direction.Vertical, update),
            self.deriv,
            Direction.Horizontal,
            update,
        )
        # Gy : lissage horizontal puis derivee verticale
        gy = convolve_1d(
            convolve_1d(grid, self.smooth, Direction.Horizontal, update),
            self.deriv,
            Direction.Vertical,
            update,
        )

        scalar, threshold = self.scalar, self.threshold
        out: Grid = []
        for row_x, row_y in zip(gx, gy):
            # le coefficient de normalisation est applique UNE seule fois
            mags = [scalar * hypot(a, b) for a, b in zip(row_x, row_y)]
            if threshold is not None:
                mags = [255.0 if m >= threshold else 0.0 for m in mags]
            out.append(mags)
            update()
        return out


# --- Sobel ---
sobel_kernel_smooth: list[float] = [1, 2, 1]
sobel_kernel_derivation: list[float] = [-1, 0, 1]
sobel_scalar = 1 / 4
sobel_threshold: float | None = 30  # None = pas de seuil


class SobelFilter(KernelFilter):
    def __init__(self):
        super().__init__(
            sobel_kernel_smooth,
            sobel_kernel_derivation,
            sobel_scalar,
            sobel_threshold,
            "Sobel",
        )


# --- Prewitt ---
prewit_kernel_smooth: list[float] = [1, 1, 1]
prewit_kernel_derivation: list[float] = [-1, 0, 1]
prewit_scalar = 1 / 3
prewit_threshold: float | None = 30  # None = pas de seuil


class PrewitFilter(KernelFilter):
    def __init__(self):
        super().__init__(
            prewit_kernel_smooth,
            prewit_kernel_derivation,
            prewit_scalar,
            prewit_threshold,
            "Prewit",
        )


# --- EM ---
em_kernel_smooth: list[float] = [1, 2, 3, 2, 1]
em_kernel_derivation: list[float] = [1, -2, 0, 2, -1]
em_scalar = 1 / 18
em_threshold: float | None = 30  # None = pas de seuil


class EMFilter(KernelFilter):
    def __init__(self):
        super().__init__(
            em_kernel_smooth, em_kernel_derivation, em_scalar, em_threshold, "Em"
        )


# --- Bruits ---
class GaussianNoiseFilter(PixelFilter):
    def __init__(self, mean: float, sigma: float) -> None:
        super().__init__("GaussianNoise")
        self.mean = mean
        self.sigma = sigma

    def compute(self, value: float) -> float:
        return min(255.0, max(0.0, value + gauss(self.mean, self.sigma)))


class SaltAndPepperNoiseFilter(PixelFilter):
    def __init__(self, odds: float):
        super().__init__("SaltAndPepperNoise")
        self.odds = odds

    def compute(self, value: float) -> float:
        noise = random()
        if noise < self.odds / 2:
            return 0.0
        if noise < self.odds:
            return 255.0
        return value
