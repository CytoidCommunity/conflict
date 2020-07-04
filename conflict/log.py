import logging

from conflict.locations import LOG_PATH


def get_logger(name):
    from conflict.config import config
    logger = logging.getLogger(name)
    logger.setLevel(config.log_level)

    if logger.hasHandlers():
        return logger

    file = LOG_PATH / f'{name}.log'
    file.touch(exist_ok=True)
    handler = logging.FileHandler(file)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
    handler.setLevel(config.log_level)
    logger.addHandler(handler)

    return logger
