import typer

# Shared Typer app for all `todo` subcommands
app = typer.Typer()
# Eagerly import subcommand modules so they register with `app`
from . import add, list, show, update, delete, calendar  # noqa: F401

