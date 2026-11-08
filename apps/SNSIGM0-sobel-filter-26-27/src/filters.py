from PIL import Image
from safe_image import SafeImage, PixelChannels
from collections.abc import Callable

class FilterContext:
    def __init__(self, image: SafeImage):
        self.image = image
        self.width, self.height = image.get_image().size
        self.x = 0
        self.y = 0

    def set_x(self, in_x: int) -> None:
        self.x = in_x

    def set_x(self, in_y: int) -> None:
        self.y = in_y

    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def set_xy(self, in_x: int, in_y:int)->None:
        self.x = in_x
        self.y = in_y

    def get_target_pixel(self)-> PixelChannels:
        return self.get_pixel(self.x, self.y)

    def get_pixel(self, x: int, y: int) -> PixelChannels:
        return PixelChannels(self.image.get_image().getpixel((x,y)))



def apply_filter(safe_image: SafeImage, filter_func: Callable[[FilterContext], None]) -> None:
    context: FilterContext = FilterContext(safe_image)
    for x in range(context.width):
        for y in range(context.height):
             context.set_xy(x,y)
             filter_func(context)



def black_and_white_filter(context: FilterContext) -> None:
    pixel: PixelChannels = context.get_target_pixel()
    if not pixel.has_rgb():
        return  # Skip pixels that don't have RGB channels

    r, g, b = pixel.get_rgb()
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)  # luminance formula
    if pixel.has_alpha():
        context.image.get_image().putpixel((context.x, context.y), (gray, gray, gray, pixel.get_alpha()))
    else:
        context.image.get_image().putpixel((context.x, context.y), (gray, gray, gray))


sobel_kernel_smooth: int[] = [1,2,1]
sobel_kernel_derivation: int[] = [-1,0,1]
def sobel_filter_horizontal(context: FilterContext) -> None:
    pass



