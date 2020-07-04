from asyncio.subprocess import create_subprocess_shell, DEVNULL
from pathlib import Path
import logging

from tenacity import retry, stop_after_attempt, before_log, before_sleep_log, wait_fixed

from conflict.config import config
from conflict.log import get_logger

try:
    import ffmpeg
except ImportError:
    ffmpeg = None

try:
    import aioboto3
    from aiobotocore.config import AioConfig
except ImportError:
    aioboto3 = None
    AioConfig = None


async def process_video(filename):
    if config.transcoding is not None:
        logger = get_logger('transcoding')
        if ffmpeg is None:
            logger.error('❌  Can NOT use transcoding. Did you forget to install \"conflict[ffmpeg]\"?')
        new_filename = str(Path(filename).with_suffix('.' + config.transcoding.format.lstrip('.')))
        cmd = ' '.join(ffmpeg.input(filename).output(new_filename).compile())
        process = await create_subprocess_shell(cmd, stdout=DEVNULL, stderr=DEVNULL)
        rtn = await process.wait()
        if rtn != 0:
            if rtn == 127:
                logger.error('❌  No ffmpeg executable found. Did you forget to install ffmpeg and/or add it to PATH?')
            else:
                logger.error('❌  Failed to run \"%s\": it returns %d', cmd, rtn)
            logger.warning('⚠️  Using original flv file.')
        else:
            if not config.transcoding.keep_origin:
                try:
                    Path(filename).unlink()
                except OSError:
                    logger.error('❌  Could not delete original file.')
                    logger.warning('⚠️  Ignored.')
            filename = new_filename

    if config.s3 is not None:
        logger = get_logger('s3')
        if aioboto3 is None:
            logger.error('❌  Can NOT use s3. Did you forget to install \"conflict[s3]\"?')

        @retry(wait=wait_fixed(config.retry_delay),
               stop=stop_after_attempt(config.s3.max_retry),
               before=before_log(logger, logging.DEBUG),
               before_sleep=before_sleep_log(logger, logging.WARNING),
               reraise=True)
        async def upload():
            async with aioboto3.resource('s3',
                                         endpoint_url=config.s3.endpoint_url,
                                         aws_access_key_id=config.s3.access_key_id,
                                         aws_secret_access_key=config.s3.secret_access_key.get_secret_value(),
                                         config=AioConfig(s3={'addressing_style': config.s3.addressing_style})) as s3:
                bucket = s3.Bucket(config.s3.bucket)
                await bucket.upload_file(filename, Path(filename).name)

        try:
            await upload()
        except:
            logger.exception('❌  无法上传至指定服务器.')
