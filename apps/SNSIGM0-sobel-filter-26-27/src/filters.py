from math import sqrt
from random import gauss, uniform

from kernel_utils import Direction, convolve_1d
from safe_image import PixelChannels, SafeImage
from throttler import set_label, update


class FilterContext:
    def __init__(self, image: SafeImage):
        self.image = image
        self.width, self.height = image.get_image().size
        self.x = 0
        self.y = 0
        self.target = image

    def set_target_as_copy(self) -> None:
        self.target = self.image.Copy()

    def set_x(self, in_x: int) -> None:
        self.x = in_x

    def set_y(self, in_y: int) -> None:
        self.y = in_y

    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def get_xy(self) -> (int, int):
        return (self.x, self.y)

    def set_xy(self, in_x: int, in_y: int) -> None:
        self.x = in_x
        self.y = in_y

    def get_target_pixel(self) -> PixelChannels:
        return self.get_pixel(self.x, self.y)

    def get_pixel(self, x: int, y: int) -> PixelChannels:
        return PixelChannels(self.target.get_image().getpixel((x, y)))


class Filter:
    def __init__(self, filter_name: str):
        self.name = filter_name

    def apply(self, image: SafeImage) -> SafeImage:
        context: FilterContext = self.create_context(image)
        set_label(f"{self.name} : {context.image.name}")
        for x in range(context.width):
            for y in range(context.height):
                context.set_xy(x, y)
                self.compute(context)
                update()

        if context.image != context.target:
            context.image.release()
        return context.target

    def create_context(self, image: SafeImage) -> FilterContext:
        return FilterContext(image)

    def compute(self, context: FilterContext) -> None:
        pass


class BlackAndWhiteFilter(Filter):
    def __init__(self):
        super().__init__("Black and White")

    def compute(self, context: FilterContext) -> None:
        pixel: PixelChannels = context.get_target_pixel()
        if not pixel.has_rgb():
            return  # Skip pixels that don't have RGB channels

        r, g, b = pixel.get_rgb()
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)  # luminance formula
        if pixel.has_alpha():
            context.target.get_image().putpixel(
                context.get_xy(), (gray, gray, gray, pixel.get_alpha())
            )
        else:
            context.target.get_image().putpixel(context.get_xy(), (gray, gray, gray))


class KernelFilter(Filter):
    """Filtre de contours separable : G = scalar * (lissage ⊗ derivee).

    Les calculs intermediaires sont faits en flottants pour garder les
    valeurs negatives et superieures a 255 ; on ne revient en 8 bits
    qu'a la fin, apres le calcul de la magnitude.
    """

    def __init__(
        self,
        smooth_kernel: list[int],
        derivation_kernel: list[int],
        scalar: float,
        filter_name: str,
    ):
        super().__init__(filter_name)
        self.smooth = smooth_kernel
        self.deriv = derivation_kernel
        self.scalar = scalar

    def apply(self, image: SafeImage) -> SafeImage:
        set_label(f"{self.name} : {image.name}")
        img = image.get_image()
        width, height = img.size
        gray: list[list[float]] = [
            [float(PixelChannels(img.getpixel((x, y))).get_first()) for x in range(width)]
            for y in range(height)
        ]

        # Gx : lissage vertical puis derivee horizontale
        gx = convolve_1d(
            convolve_1d(gray, self.smooth, Direction.Vertical, update),
            self.deriv,
            Direction.Horizontal,
            update,
        )
        # Gy : lissage horizontal puis derivee verticale
        gy = convolve_1d(
            convolve_1d(gray, self.smooth, Direction.Horizontal, update),
            self.deriv,
            Direction.Vertical,
            update,
        )

        result: SafeImage = image.Copy(f"{self.name}_{image.name}")
        out = result.get_image()
        for y in range(height):
            for x in range(width):
                # le coefficient de normalisation est applique UNE seule fois
                mag = self.scalar * sqrt(gx[y][x] ** 2 + gy[y][x] ** 2)
                pix = min(255, int(mag))
                out.putpixel((x, y), (pix, pix, pix))
            update()

        image.release()  # sans effet si l'image est verrouillee
        return result


sobel_kernel_smooth = [1, 2, 1]
sobel_kernel_derivation = [-1, 0, 1]
sobel_scalar = 1 / 4


class SobleFilter(KernelFilter):
    def __init__(self):
        super().__init__(
            sobel_kernel_smooth, sobel_kernel_derivation, sobel_scalar, "Sobel"
        )


prewit_kernel_smooth: list[int] = [1, 1, 1]
prewit_kernel_derivation: list[int] = [-1, 0, 1]
prewit_scalar = 1 / 3


class PrewitFilter(KernelFilter):
    def __init__(self):
        super().__init__(
            prewit_kernel_smooth, prewit_kernel_derivation, prewit_scalar, "Prewit"
        )


em_kernel_derivation: list[int] = [1, -2, 0, 2, -1]
em_kernel_smooth: list[int] = [1, 2, 3, 2, 1]
em_scalar = 1 / 18


class EMFilter(KernelFilter):
    def __init__(self):
        super().__init__(em_kernel_smooth, em_kernel_derivation, em_scalar, "Em")


class GaussianNoiseFilter(Filter):
    def __init__(self, mean: float, sigma: float) -> None:
        super().__init__("GaussianNoise")
        self.mean = mean
        self.sigma = sigma

    def create_context(self, image: SafeImage) -> FilterContext:
        context = super().create_context(image)
        context.set_target_as_copy()
        return context

    def compute(self, context: FilterContext) -> None:
        noise: float = gauss(self.mean, self.sigma)
        raw_pix: int = context.get_target_pixel().get_first()
        pix: float = raw_pix + noise
        if pix > 255:
            pix = 255
        elif pix < 0:
            pix = 0

        pix = int(pix)
        context.target.get_image().putpixel(context.get_xy(), (pix, pix, pix))


class SaltAndPepperNoiseFilter(Filter):
    def __init__(self, odds: float):
        super().__init__("SaltAndPepperNoise")
        self.odds = odds

    def create_context(self, image: SafeImage) -> FilterContext:
        context = super().create_context(image)
        context.set_target_as_copy()
        return context

    def compute(self, context: FilterContext) -> None:
        noise: float = uniform(0.0, 1.0)
        pix: int = 0
        if noise < (self.odds / 2):
            pix = 0
        elif noise < self.odds:
            pix = 255
        else:
            return

        context.target.get_image().putpixel(context.get_xy(), (pix, pix, pix))


class ThresholdFilter(Filter):
    def __init__(self, threshold: int):
        super().__init__("Threshold")
        self.threshold = threshold

    def compute(self, context: FilterContext) -> None:
        pix: int = context.get_target_pixel().get_first()
        pix = 255 if pix >= self.threshold else 0
        context.target.get_image().putpixel(context.get_xy(), (pix, pix, pix))
