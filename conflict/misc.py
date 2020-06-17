import asyncio
import functools
import sys


def auto_retry(logger=None, delay: int = 3):
    if not logger:
        import logging
        logger = logging.getLogger()
        if not logger.hasHandlers():
            logger.addHandler(logging.NullHandler())

    def decorator(func):
        try:
            name = func.__name__
        except AttributeError:
            name = "unknown"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            output_args = [str(i) for i in args] + [f"{k}={v}" for k, v in kwargs.items()]
            output_name = '%s(%s)' % (name, ', '.join(output_args))
            retries = 0
            while True:
                if retries > 0:
                    logger.warning("⏳  Retrying: `%s`, attempts = %d", output_name, retries)
                try:
                    res = await func(*args, **kwargs)
                except:
                    logger.exception(
                        "⚠️  An error occurred while running `%s`:", output_name)
                    await asyncio.sleep(delay)
                    retries += 1
                else:
                    break
            logger.debug("☑️  Successfully run `%s` after %d retries.", output_name, retries)
            return res

        return wrapper

    return decorator
