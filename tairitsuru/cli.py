# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import sys

import click

from .misc import ComplexCLI, pass_environment, verbosity_option


@click.command(cls=ComplexCLI)
@click.version_option()
@pass_environment
@verbosity_option
def cli(ctx):
    """
    Tairitsuru is an automatic Bilibili livestream capturing tool.

    This is the main command line entry of tairitsuru.
    """
    pass
