from image_manipulation import *
from pathlib import Path
from file_utils import is_image_supported
from config_loader import config


def process_image(file_path: Path) -> None:
    image = load_image(file_path)
    # Here you can apply any image processing operations, e.g., Sobel filter
    # For demonstration, we will just save the original image to the output directory
    output_file_path = config.output_path / file_path.name
    save_image(image, output_file_path)
    pass


for element in config.input_path.iterdir():
    if is_image_supported(element):
        process_image(element)

input("Processing complete. Press Enter to exit...")