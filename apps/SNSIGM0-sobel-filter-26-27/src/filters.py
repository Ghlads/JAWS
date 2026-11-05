from PIL import Image
from safe_image import SafeImage, PixelChannels

def black_and_white_filter(safe_image: SafeImage) -> None:
    width, height = safe_image.get_image().size
    for x in range(width):
        for y in range(height):
            pixel: PixelChannels = PixelChannels(safe_image.get_image().getpixel((x, y)))
            if not pixel.has_rgb():
                continue  # Skip pixels that don't have RGB channels

            r, g, b = pixel.get_rgb()
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)  # luminance formula
            if pixel.has_alpha():
                safe_image.get_image().putpixel((x, y), (gray, gray, gray, pixel.get_alpha()))
            else:
                safe_image.get_image().putpixel((x, y), (gray, gray, gray))
    pass