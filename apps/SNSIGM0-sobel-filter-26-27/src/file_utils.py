from pathlib import Path
from config_loader import config

def is_image_supported(file_path: Path) -> bool:
    return file_path.is_file() and file_path.suffix.lower() in config.supported_extensions