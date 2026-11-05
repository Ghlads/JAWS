from image_manipulation import *
from pathlib import Path
from file_utils import is_image_supported
from config_loader import config
from filters import black_and_white_filter


def process_image(file_path: Path) -> None:
    image: SafeImage = load_image(file_path)
    black_and_white_filter(image)
    # do filtering things here
    
    output_file_path = config.output_path / file_path.name
    save_image(image, output_file_path)
    image.release()  # Release the image resource after processing
    pass


for element in config.input_path.iterdir():
    if is_image_supported(element):
        process_image(element)

input("Processing complete. Press Enter to exit...")