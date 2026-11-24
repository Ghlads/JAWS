from pathlib import Path

from config_loader import config
from file_utils import is_image_supported
from filters import *
from image_manipulation import load_image, save_image
from throttler import done


def make_path(file_path: Path, filter_name: str) -> Path:
    return config.output_path / file_path.stem / (filter_name + "_" + file_path.name)


def process_image(file_path: Path) -> None:
    name = file_path.name
    baw = load_image(file_path)  # deja en niveaux de gris

    sources: list[tuple[str, Grid]] = [
        ("", baw),
        ("_gauss", GaussianNoiseFilter(0, 30).apply(baw, name)),
        ("_sap", SaltAndPepperNoiseFilter(0.2).apply(baw, name)),
    ]
    edge_filters: list[tuple[str, Filter]] = [
        ("sobel", SobelFilter()),
        ("prewit", PrewitFilter()),
        ("em", EMFilter()),
    ]

    for suffix, source in sources:
        save_image(source, make_path(file_path, "baw" + suffix))
        for prefix, edge_filter in edge_filters:
            result = edge_filter.apply(source, name + suffix)
            save_image(result, make_path(file_path, prefix + suffix))


for element in config.input_path.iterdir():
    if is_image_supported(element):
        process_image(element)

done("Processing complete")
input("Press Enter to exit...")
