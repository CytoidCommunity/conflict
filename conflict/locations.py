from pathlib import Path

from appdirs import AppDirs

loc = AppDirs("conflict", "CytoidCommunity")
CACHE_PATH = Path(loc.user_cache_dir)
CONFIG_PATH = Path(loc.user_config_dir)
DATA_PATH = Path(loc.user_data_dir)
LOG_PATH = Path(loc.user_log_dir)

for path in [CACHE_PATH, CONFIG_PATH, DATA_PATH, LOG_PATH]:
    path.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = CONFIG_PATH / 'config.toml'
CONFIG_FILE.touch(exist_ok=True)
