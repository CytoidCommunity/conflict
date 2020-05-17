from cleo import Command
from tomlkit.exceptions import ParseError


class CheckCommand(Command):
    name = "check"
    description = "Verify your configuration file"
    help = "This will verify your configuration file, and show the errors " \
           "if exists. No output if everything is ok."

    _errors = []

    def error(self, text):
        self._errors.append(text)

    def end(self):
        if len(self._errors) == 0:
            return 0
        for err in self._errors:
            self.line_error(err, "error")
        return -1

    def handle(self):
        try:
            from ...config import config
        except ParseError as e:
            self.error(str(e) + "\nInvalid TOML file format.")
            return self.end()

        # Proxy
        proxy = config.get("proxy")
        if proxy:
            try:
                from httpx import Proxy
                _ = Proxy(proxy['url'])
            except KeyError:
                self.error("Using proxy, but no url is given.")
            except TypeError:
                self.error("\"proxy\" is not a table.")
            except ValueError as e:
                self.error(e.args)

        # Watchers
        watchers = config.get("watchers")
        if not watchers:
            self.error("No watchers configured.")

        return self.end()
