from pydantic import ValidationError
import toml
import typer

from conflict.locations import CONFIG_FILE
from conflict.schema.config import Config

app = typer.Typer()


@app.command()
def cat():
    """
    Display the current configuration.
    """
    with CONFIG_FILE.open() as f:
        typer.echo(f.read())


@app.command()
def check(file: typer.FileText = typer.Argument(CONFIG_FILE, help='The configuration file to check.')):
    """
    Check if the given configuration file is valid.
    """
    with file:
        content = file.read()
    try:
        config = toml.loads(content)
        Config(**config)
    except toml.TomlDecodeError as e:
        typer.echo('', err=True)
        typer.echo(' ' * 2 + str(e), err=True)
        typer.echo('', err=True)
        typer.echo('Invalid TOML file format.', err=True)
        raise typer.Abort()
    except ValidationError as e:
        typer.echo('', err=True)
        typer.echo(str(e), err=True)
        typer.echo('', err=True)
        typer.echo('Invalid configuration file.', err=True)
        raise typer.Abort()


@app.command()
def load(file: typer.FileText = typer.Argument(..., help='The new configuration file to load.')):
    """
    Load new configuration file.
    """
    with file:
        content = file.read()
    try:
        config = toml.loads(content)
        Config(**config)
    except toml.TomlDecodeError as e:
        typer.echo('', err=True)
        typer.echo(' ' * 2 + str(e), err=True)
        typer.echo('', err=True)
        typer.echo('Invalid TOML file format.', err=True)
        raise typer.Abort()
    except ValidationError as e:
        typer.echo('', err=True)
        typer.echo(str(e), err=True)
        typer.echo('', err=True)
        typer.echo('Invalid configuration file.', err=True)
        raise typer.Abort()
    with CONFIG_FILE.open(mode='w') as f:
        f.write(content)
