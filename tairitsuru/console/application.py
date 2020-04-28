from cleo import Application

from tairitsuru.__version__ import __version__

application = Application("tairitsuru", __version__)

if __name__ == "__main__":
    application.run()
