from cleo import Command, option


class DaemonCommand(Command):
    name = "daemon"
    description = "Start conflict daemon"
    help = "This will automatically read your configuration file and start " \
           "watching as long as your configuration file is valid."
    options = [option("--no-capture", None, "Do not capture")]

    def handle(self):
        rtn = self.call_silent("check")
        if rtn != 0:
            self.line_error("Invalid configuration file. Try:", "error")
            self.line_error("")
            self.line_error("  conflict check", "info")
            self.line_error("")
            return rtn

        from ...config import config
        watchers = config.get("watchers")
        import asyncio
        from ...live.core import Worker
        coros = []
        for watcher in watchers:
            if watcher.get("live"):
                live_conf = watcher["live"]
                capture = live_conf.get("capture", False)
                if self.option("no-capture"):
                    capture = False
                worker = Worker(live_conf["roomid"], capture, watcher.get("interval", 60))
                if watcher.get("push"):
                    from ...push import live_start, live_end

                    @worker.on_start
                    async def _(arg):
                        if watcher.get("nickname"):
                            arg = {**arg, "user_name": watcher["nickname"]}
                        await asyncio.gather(*[live_start(id_, arg) for id_ in watcher["push"]])

                    @worker.on_end
                    async def _(arg):
                        if watcher.get("nickname"):
                            arg = {**arg, "user_name": watcher["nickname"]}
                        await asyncio.gather(*[live_end(id_, arg) for id_ in watcher["push"]])
                coros.append(worker.run())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*coros))
