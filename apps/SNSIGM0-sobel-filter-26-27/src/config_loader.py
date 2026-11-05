from pathlib import Path
from yaml import safe_load

class Config:
    input_path: Path
    output_path: Path
    supported_extensions: list[str]


    def __init__(self, root_path: Path, config_file: str):
        with open(root_path / config_file, "r") as file:
            config_data = safe_load(file)
        print("config loaded:")
        self.input_path = root_path / config_data["config"]["input_dir"]
        self.output_path = root_path / config_data["config"]["output_dir"]
        self.supported_extensions = config_data["config"]["supported_extensions"]

config = Config(Path.cwd(), "config.yml")