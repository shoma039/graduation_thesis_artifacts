import typer
from src.cli import commands

app = typer.Typer()

app.add_typer(commands.app, name="todo")


def main():
    app()


if __name__ == "__main__":
    main()
