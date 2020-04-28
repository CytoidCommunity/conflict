"""
Provide logger helper.

Any other modules in tairitsuru should use `Logger` from this module to log messages.
"""
import logging
import pathlib
import sys

from .locations import LOG_DIR


def Logger(name, console_level=logging.WARNING, file_level=logging.INFO):

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        return logger

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter("[%(asctime)s %(name)s] %(levelname)s: %(message)s"))
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    log_path = pathlib.Path(LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)
    log_file_path = log_path / f"{name}.log"
    log_file_path.touch(exist_ok=True)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)

    return logger
