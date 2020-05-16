from cleo import Command, option


class DaemonCommand(Command):
    name = "daemon"
    description = "Start tairitsuru daemon"
    help = "This will automatically read your configuration file and start " \
           "watching as long as your configuration file is valid."
    options = [option("--no-capture", None, "Do not capture")]

    def handle(self):
        rtn = self.call_silent("check")
        if rtn != 0:
            self.line_error("Invalid configuration file. Try:", "error")
            self.line_error("")
            self.line_error("  tairitsuru check", "info")
            self.line_error("")
            return rtn

        from tairitsuru.config import config
        proxy_url = None
        if config.get('proxy'):
            proxy_url = config['proxy']['url']
        watchers = config.get("watchers")
        import asyncio
        from tairitsuru.live.core import Worker
        coros = []
        for watcher in watchers:
            if watcher.get("live"):
                live_conf = watcher["live"]
                worker = Worker(live_conf["roomid"], live_conf.get('record'), watcher.get('interval'), proxy_url)
                coros.append(worker.run())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*coros))
