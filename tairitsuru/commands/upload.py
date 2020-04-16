# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio

import click

from tairitsuru.cli import pass_environment, verbosity_option
from tairitsuru.utils.upload import upload


@click.command("upload")
@click.argument("targets", nargs=-1, type=click.Path(exists=True))
@click.option("-e", "--endpoint", envvar="S3_ENDPOINT", required=True,
              help="A S3-compatible object storage endpoint. \
                    Can be set using S3_ENDPOINT environment variable.")
@click.option("-b", "--bucket", envvar="S3_BUCKET", required=True,
              help="The name of a S3-compatible object storage bucket. \
                    Can be set using S3_BUCKET environment variable.")
@click.option("--access-key", envvar="S3_ACCESS_KEY", required=True,
              help="The access key of the object storage. \
                    Can be set using S3_ACCESS_KEY environment variable.")
@click.option("--access-secret", envvar="S3_ACCESS_SECRET", required=True,
              help="The access secret of the object storage. \
                    Can be set using S3_ACCESS_SECRET environment variable.")
@click.option("--addr-style", default="auto", show_default=True,
              help="The addressing style of the object storage.")
@pass_environment
@verbosity_option
def cli(ctx, targets, endpoint, bucket, access_key, access_secret, addr_style):
    """
    The file upload helper.

    Upload the file(s)/directory(ies) provided to a S3-compatible object storage.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        upload(targets, endpoint, bucket, access_key, access_secret, addr_style, ctx))
