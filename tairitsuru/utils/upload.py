# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import logging

from aioboto3 import Session
from aiobotocore.config import AioConfig


async def upload(endpoint, file, bucket, access_key, access_secure, addr_style):
    session = Session(
        aws_access_key_id = access_key,
        aws_secret_access_key = access_secure,
    )
    try:
        async with session.resource(
            "s3",
            endpoint_url = endpoint,
            config = AioConfig(
                s3 = {
                    "addressing_style": addr_style
                }
            )
        ) as s3:
            bucket = await s3.Bucket(bucket)
            with open(file, mode="rb") as f:
                await bucket.upload_fileobj(f)
    except Exception:
        logging.exception("An error occurred while uploading:")
        sys.exit(1)
    else:
        logging.info("Success!")
