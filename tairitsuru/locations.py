import sys

from appdirs import AppDirs

appdir = AppDirs("tairitsuru", "CytoidCommunity")

CACHE_DIR = appdir.user_cache_dir
CONFIG_DIR = appdir.user_config_dir
DATA_DIR = appdir.user_data_dir
LOG_DIR = appdir.user_log_dir
