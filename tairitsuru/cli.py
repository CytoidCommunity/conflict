import asyncio
import logging

import click


@click.group()
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    """
    Tairitsuru is a automatic Bilibili livestream capturing tool.

    This is the main command line entry for tairitsuru.
    """
    if verbose == True:
        logging.info("You are now in verbose mode.")
        ctx["verbose"] = verbose


@cli.command()
@click.argument("filename", type=click.File('rb'))
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
def upload(filename, endpoint, bucket, access_key, access_secure, addr_style):
    """
    The file upload helper. Upload the file provided to a S3-compatible object storage.
    """
    from .utils.upload import upload
    asyncio.run(upload(endpoint, filename, bucket,
                       access_key, access_secure, addr_style))
