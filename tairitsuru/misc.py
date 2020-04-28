import asyncio
import functools


def auto_retry(max_retries: int = 3, delay: int = 1, logger=None):
    if not logger:
        import logging
        logger = logging.getLogger()
        if not logger.hasHandlers():
            logger.addHandler(logging.NullHandler())

    def decorator(func):
        try:
            name = func.__name__
        except:
            name = "unknown"

        @functools.wraps(func)
        async def warpper(*args, **kwargs):
            output_args = [str(i) for i in args
                           ] + [f"{k}={v}" for k, v in kwargs.items()]
            output_name = '%s(%s)' % (name, ', '.join(output_args))
            retries = 0
            while retries <= max_retries:
                if retries > 0:
                    logger.warning("⏳  Retrying: `%s`, attempts = %d/%d",
                                   output_name, retries, max_retries)
                try:
                    res = await func(*args, **kwargs)
                except:
                    logger.exception(
                        "⚠️  An error occurred while running `%s`:",
                        output_name)
                    await asyncio.sleep(delay)
                    retries += 1
                else:
                    break
            if retries <= max_retries:
                logger.info("☑️  Successfully run `%s` after %d retries.",
                            output_name, retries)
                return res
            else:
                logger.error("❌  Failed to run `%s`: max retry count reached.",
                             output_name)
                return None

        return warpper

    return decorator
