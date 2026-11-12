from math import sqrt
from random import gauss, uniform

from kernel_utils import Direction, mean, sample_kernel
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
        set_label("{name} : {image}".format(name=self.name, image=context.image.name))
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


class KernelDirectionalFilter(Filter):
    def __init__(self, kernel: list[float], direction: Direction, filter_name: str):
        super().__init__(filter_name)
        self.kernel = kernel
        self.direction = direction

    def create_context(self, image: SafeImage) -> FilterContext:
        context: FilterContext = FilterContext(image)
        context.set_target_as_copy()
        return context

    def compute(self, context: FilterContext) -> None:
        pixel_mean: int = int(
            mean(
                sample_kernel(
                    context.image, context.get_xy(), self.kernel, self.direction
                )
            )
        )
        context.target.get_image().putpixel(
            context.get_xy(), (pixel_mean, pixel_mean, pixel_mean)
        )


class HorizontalKernelFilter(KernelDirectionalFilter):
    def __init__(self, kernel: list[float], filter_name: str):
        super().__init__(kernel, Direction.Horizontal, filter_name)


class VerticalKernelFilter(KernelDirectionalFilter):
    def __init__(self, kernel: list[float], filter_name: str):
        super().__init__(kernel, Direction.Vertical, filter_name)


class BidirectionalKernelFilter(Filter):
    def __init__(
        self,
        horizontal_filter: HorizontalKernelFilter,
        vertical_filter: VerticalKernelFilter,
    ):
        super().__init__("BidirectionalKernelFilter")
        self.horizontal_filter = horizontal_filter
        self.vertical_filter = vertical_filter

    def apply(self, image) -> SafeImage:
        return self.vertical_filter.apply(self.horizontal_filter.apply(image))


class KernelFilter(Filter):
    def __init__(
        self, smooth_kernel: list[int], derivation_kernel: list[int], filter_name: str
    ):
        self.first_pass: BidirectionalKernelFilter = BidirectionalKernelFilter(
            HorizontalKernelFilter(
                smooth_kernel, "First_{name}_Horizontal".format(name=filter_name)
            ),
            VerticalKernelFilter(
                derivation_kernel, "First_{name}_Vertical".format(name=filter_name)
            ),
        )
        self.second_pass: BidirectionalKernelFilter = BidirectionalKernelFilter(
            HorizontalKernelFilter(
                derivation_kernel, "Second_{name}_Horizontal".format(name=filter_name)
            ),
            VerticalKernelFilter(
                smooth_kernel, "Second_{name}_Vertical".format(name=filter_name)
            ),
        )

    def apply(self, image: SafeImage) -> SafeImage:
        image.lock()
        result = self.compute_magnitude(
            self.first_pass.apply(image), self.second_pass.apply(image)
        )
        image.unlock()
        image.release()
        return result

    def compute_magnitude(self, first: SafeImage, second: SafeImage) -> SafeImage:
        width: int = first.get_image().width
        height: int = first.get_image().height
        merged: SafeImage = first.Copy()
        for x in range(width):
            for y in range(height):
                first_pix: int = PixelChannels(
                    first.get_image().getpixel((x, y))
                ).get_first()
                second_pix: int = PixelChannels(
                    second.get_image().getpixel((x, y))
                ).get_first()
                new_pix: int = int(
                    sqrt(first_pix * first_pix + second_pix * second_pix)
                )
                merged.get_image().putpixel((x, y), (new_pix, new_pix, new_pix))

        first.release()
        second.release()
        return merged


sobel_kernel_smooth = [1, 2, 1]
sobel_kernel_derivation = [-1, 0, 1]


class SobleFilter(KernelFilter):
    def __init__(self):
        super().__init__(sobel_kernel_smooth, sobel_kernel_derivation, "Sobel")


prewit_kernel_smooth: list[int] = [1, 1, 1]
prewit_kernel_derivation: list[int] = [-1, 0, 1]


class PrewitFilter(KernelFilter):
    def __init__(self):
        super().__init__(prewit_kernel_smooth, prewit_kernel_derivation, "Prewit")


em_kernel_derivation: list[int] = [1, -2, 0, 2, -1]
em_kernel_smooth: list[int] = [1, 2, 3, 2, 1]


class EMFilter(KernelFilter):
    def __init__(self):
        super().__init__(em_kernel_smooth, em_kernel_derivation, "Em")


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
