# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import sys

import click


class Environment(logging.Logger):

    def __init__(self):
        logging.Logger.__init__(self, "tairitsuru", logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s %(name)s] %(levelname)s: %(message)s"
        ))
        self.addHandler(handler)
        self._verbose = False
        self._quiet = False

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self._verbose = value
        if value:
            if self._quiet:
                raise click.UsageError("Can NOT be verbose and quiet at the same time.")
            self.setLevel(logging.DEBUG)

    @property
    def quiet(self):
        return self._verbose

    @quiet.setter
    def quiet(self, value):
        self._quiet = value
        if value:
            if self._verbose:
                raise click.UsageError("Can NOT be verbose and quiet at the same time.")
            self.setLevel(logging.ERROR)

    def progressbar(self, *args, **kwargs):
        bar = click.progressbar(*args, **kwargs)
        if self.quiet:
            bar.is_hidden = True
        return bar


pass_environment = click.make_pass_decorator(Environment, ensure=True)


class ComplexCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        cmd_folder = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "commands"))
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and not filename.startswith("_"):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode("ascii", "replace")
            mod = __import__(
                "tairitsuru.commands.{}".format(name), None, None, ["cli"]
            )
        except ImportError:
            return
        return mod.cli


def verbosity_option(func):
    def verbose(func):
        def callback(ctx, param, value):
            env = ctx.ensure_object(Environment)
            if value:
                env.verbose = True
            return value
        return click.option("-v", "--verbose", is_flag=True,
                             expose_value=False,
                             help="Enables verbosity.",
                             callback=callback)(func)

    def quiet(func):
        def callback(ctx, param, value):
            env = ctx.ensure_object(Environment)
            if value:
                env.quiet = True
            return value
        return click.option("-q", "--quiet", is_flag=True,
                             expose_value=False,
                             help="Quiet mode.",
                             callback=callback)(func)

    func = verbose(func)
    func = quiet(func)
    return func
