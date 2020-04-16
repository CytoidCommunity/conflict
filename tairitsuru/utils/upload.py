# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import logging
import os
import sys
import threading
from asyncio import sleep
from typing import AnyStr, Iterable, Optional, Tuple

from aioboto3 import Session
from aiobotocore.config import AioConfig

_logger: Optional[logging.Logger] = None


def _check_logger(logger=None):
    global _logger
    _logger = logger

    if not _logger:
        _logger = logging.Logger(__name__, logging.INFO)


async def _get_etag(bucket, key):
    async for obj in bucket.objects.filter(Prefix=key):
        if obj.key == key:
            return await obj.e_tag
    return None


class S3Progress:

    def __init__(self, filename, logger):
        self.filename = filename
        self.size = os.path.getsize(filename)
        self.bytes_amount = 0
        if logger.progressbar:
            self.progressbar = logger.progressbar(
                length=self.size, label=filename)
        else:
            self.progressbar = None
        self.lock = threading.Lock()

    def __call__(self, sent_bytes):
        with self.lock:
            if self.progressbar:
                if self.bytes_amount == 0:
                    self.progressbar.__enter__()

                self.progressbar.update(sent_bytes - self.bytes_amount)

                if sent_bytes == self.size:
                    self.progressbar.__exit__(None, None, None)
            self.bytes_amount = sent_bytes


MAX_RETRIES = 5
RETRY_DELAY = 1


async def _upload(bucket, file: AnyStr, retries: int = 0) -> bool:

    key = os.path.basename(file)
    if await _get_etag(bucket, key):
        _logger.info("⚠️ %s already exists. Overwriting...", key)

    if retries > MAX_RETRIES:
        _logger.error("❌ Failed: %s, max retry count reached.", key)
        return False

    if retries:
        _logger.info(
            "⏳ Retrying: %s, attempts = %d/%d", key, retries, MAX_RETRIES)
    else:
        _logger.info("⏳ Uploading: %s", key)

    try:
        await bucket.upload_file(file, key, Callback=S3Progress(file, _logger))
    except:
        _logger.exception("⚠️ An error occurred while uploading %s:", key)

    etag = await _get_etag(bucket, key)
    if etag:
        _logger.info("☑️ Uploaded: %s, etag = %s", key, etag)
        return True

    await sleep(RETRY_DELAY)
    return await _upload(bucket, file, retries + 1)


def _filter_files(targets: Iterable[AnyStr]):
    for target in targets:
        if os.path.isdir(target):
            for i in glob.glob(os.path.join(target, "**"), recursive=True):
                if os.path.isfile(i):
                    yield i
        else:
            yield target


async def upload(
        targets: Iterable[AnyStr],
        endpoint: str,
        bucket: str,
        access_key: str,
        access_secret: str,
        addr_style: Optional[str] = "auto",
        logger: Optional[logging.Logger] = None
    ) -> Tuple[int, int]:
    """Upload the file(s) provided to a S3-compatible object storage.

    Args:
        targets: An iterable that contains everything you want to upload.
        endpoint: A S3-compatible object storage endpoint.
        bucket: The name of a S3-compatible object storage bucket.
        access_key: The access key of the object storage.
        access_secret: The access secret of the object storage.
        addr_style: The addressing style of the object storage.
                               The default is `auto`.
        logger: A Logger object.  If not provided we will create one.

    Returns:
        A tuple contains the number of files which are uploaded successfully
        and the total number of files.
    """

    _check_logger(logger)

    files = _filter_files(targets)

    _logger.debug(
        "Creating session with specified access key and secret...")
    session = Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret,
    )

    try:
        _logger.debug("Connecting to the object storage...")
        async with session.resource(
                "s3",
                endpoint_url=endpoint,
                config=AioConfig(
                    s3={
                        "addressing_style": addr_style
                    }
                )
            ) as s3:

            _logger.debug("Getting bucket...")
            bucket = await s3.Bucket(bucket)

            n_success = 0
            n_total = 0
            for file in files:
                n_success += await _upload(bucket, file)
                n_total += 1
    except:
        _logger.exception("⚠️ An error occurred while uploading:")
        sys.exit(1)

    if n_total > 0:
        _logger.info("✅ All done.")
        _logger.info("%s Success = %d / Total = %d.",
                     "🎉" if n_success == n_total else "🤨", n_success, n_total)
    else:
        _logger.info("☑ Nothing to upload.")

    return (n_success, n_total)
