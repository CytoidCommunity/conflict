from cleo import Application

from tairitsuru.__version__ import __version__

from .commands.check import CheckCommand
from .commands.daemon import DaemonCommand

application = Application("tairitsuru", __version__)
application.add(CheckCommand())
application.add(DaemonCommand())

if __name__ == "__main__":
    application.run()
