# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import sys

import click

@click.group()
@click.version_option()
def cli(ctx):
    """
    Tairitsuru is an automatic Bilibili watcher.

    This is the main command line entry of tairitsuru.
    """
    pass
