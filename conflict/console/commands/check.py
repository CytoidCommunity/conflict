from cleo import Command
from tomlkit.exceptions import ParseError


def validate_url(url):
    from rfc3986.api import uri_reference
    from rfc3986.exceptions import ValidationError
    from rfc3986.validators import Validator
    validator = Validator().require_presence_of('scheme', 'host').allow_schemes('http', 'https')
    try:
        validator.validate(uri_reference(url))
    except ValidationError as e:
        return e[0]


class CheckCommand(Command):
    name = "check"
    description = "Verify your configuration file"
    help = "This will verify your configuration file, and show the errors " \
           "if exists. No output if everything is ok."

    _msgs = []

    def log(self, text, verbosity="error"):
        self._msgs.append((text, verbosity))

    def exit(self):
        flag = 0
        for text, verbosity in self._msgs:
            if verbosity == "error":
                flag = -1
            self.line(text, verbosity)
        return flag

    def handle(self):
        try:
            from ...config import config
        except ParseError as e:
            self.log(e[0])
            self.log("Invalid TOML file format.")
            return self.exit()

        # Watchers
        watchers = config.get("watchers")
        if not watchers:
            self.log("No watchers configured.")
        else:
            for watcher in watchers:
                # Push
                if watcher.get("push") is not None:
                    for push in watcher.get("push"):
                        pass

        # getPlayUrl
        get_play_url = config.get("get_play_url")
        if get_play_url is not None:
            res = validate_url(get_play_url.get("url"))
            if res:
                self.log(res)
                self.log("Invalid URL for get_play_url.")

        return self.exit()
