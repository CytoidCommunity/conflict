import atexit
from pathlib import Path

from tomlkit.toml_file import TOMLFile

from .locations import CONFIG_DIR


class ConfigFile(TOMLFile):
    def __init__(self):
        config_path = Path(CONFIG_DIR)
        config_path.mkdir(parents=True, exist_ok=True)
        config_file_path = config_path / "config.toml"
        config_file_path.touch(exist_ok=True)
        super().__init__(config_file_path)


config_file = ConfigFile()
config = config_file.read()


@atexit.register
def _():
    config_file.write(config)
