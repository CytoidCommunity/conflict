import asyncio

from pydantic import ValidationError
import toml
import typer

from conflict.config import load_conf
from conflict.locations import CONFIG_FILE

import conflict.console.config as config_cmd

app = typer.Typer(name='conflict', help='A wonderful Bilibili Live automatic watcher.')
app.add_typer(config_cmd.app, name='config', help='Manage conflict\'s configurations.')


@app.command()
def daemon(conf: typer.FileText = typer.Option(CONFIG_FILE, '--conf', '-c', help='The configuration file.')):
    """
    Start conflict watching daemon.
    """
    with conf:
        content = conf.read()
    try:
        load_conf(toml.loads(content))
    except (toml.TomlDecodeError, ValidationError):
        typer.echo('Error: Invalid configuration file.', err=True)
        typer.echo('Please check it first.', err=True)
        raise typer.Abort()

    from conflict.config import config
    from conflict.core.live import Worker
    coros = []
    for watcher in config.watchers:
        worker = Worker(watcher)
        coros.append(worker.run())
    loop = asyncio.get_event_loop()
    typer.echo('Starting conflict daemon...')
    loop.run_until_complete(asyncio.gather(*coros))
