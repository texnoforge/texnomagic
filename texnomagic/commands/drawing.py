from pathlib import Path

import click

from texnomagic.console import console
from texnomagic import cli_common
from texnomagic.drawing import TexnoMagicDrawing


@click.group()
@click.help_option('-h', '--help', help='Show command help.')
def drawing():
    """
    Manage TexnoMagic drawings.

    A drawings is a series of curves defined by 2D points.

    They are usually stored as simple CSV files.
    """


@drawing.command()
@click.argument('drawing', nargs=-1, required=True)
def show(drawing):
    """
    Show details of TexnoMagic drawing(s).

    Select one or more drawing CSV files as arguments.

    Use `texnomagic drawing list` to work on symbols instead of files.
    """
    drawings = []
    for d in drawing:
        drawing_path = Path(d)
        if not drawing_path.exists():
            console.log(f"[red]Drawing file not found[/]: [white]{d}[/]")
            continue
        dr = TexnoMagicDrawing(drawing_path)
        drawings.append(dr)

    cli_common.print_drawings(drawings)


@drawing.command()
@click.argument('symbol', required=False)
def list(symbol):
    """
    List all drawing in a TexnoMagic symbol.

    By default, tries to detect symbol from current directory.

    Select a specific symbol by passing ALPHABET/SYMBOL string.
    """
    _symbol = cli_common.get_symbol_or_fail(symbol)
    _symbol.load()

    cli_common.print_drawings(_symbol.drawings)



TEXNOMAGIC_CLI_COMMANDS = [drawing]
