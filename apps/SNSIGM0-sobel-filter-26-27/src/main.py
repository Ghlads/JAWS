from pathlib import Path

from config_loader import config
from file_utils import is_image_supported
from filters import *
from image_manipulation import load_image, save_image
from throttler import done


def make_path(file_path: Path, filter_name: str) -> Path:
    return config.output_path / file_path.stem / (filter_name + "_" + file_path.name)


def process_image(file_path: Path) -> None:
    to_save: list[(SafeImage, str)] = []
    baw_image = BlackAndWhiteFilter().apply(load_image(file_path))
    baw_image.lock()
    sobel = SobleFilter()
    prewit = PrewitFilter()
    em = EMFilter()

    to_save.append((baw_image, "baw"))
    # do filtering things here
    to_save.append((sobel.apply(baw_image), "sobel"))
    to_save.append((prewit.apply(baw_image), "prewit"))
    to_save.append((em.apply(baw_image), "em"))

    baw_gauss_image = GaussianNoiseFilter(0, 30).apply(baw_image)
    baw_sap_image = SaltAndPepperNoiseFilter(0.2).apply(baw_image)
    baw_gauss_image.lock()
    baw_sap_image.lock()

    to_save.append((baw_gauss_image, "baw_gauss"))
    to_save.append((baw_sap_image, "baw_sap"))

    to_save.append((sobel.apply(baw_gauss_image), "sobel_gauss"))
    to_save.append((prewit.apply(baw_gauss_image), "prewit_gauss"))
    to_save.append((em.apply(baw_gauss_image), "em_gauss"))

    to_save.append((sobel.apply(baw_sap_image), "sobel_sap"))
    to_save.append((prewit.apply(baw_sap_image), "prewit_sap"))
    to_save.append((em.apply(baw_sap_image), "em_sap"))

    baw_image.unlock()
    baw_gauss_image.unlock()
    baw_sap_image.unlock()

    for image_filter in to_save:
        save_image(image_filter[0], make_path(file_path, image_filter[1]))
        image_filter[0].release()  # Release the image resource after processing


for element in config.input_path.iterdir():
    if is_image_supported(element):
        process_image(element)

done("Processing complete")
input("Press Enter to exit...")
