from pathlib import Path

import click

from texnomagic import common
from texnomagic import cli_common
from texnomagic import drawing as drawing_mod


@click.group()
@click.help_option('-h', '--help', help='Show command help.')
def drawing():
    """
    Manage TexnoMagic drawings.

    A drawings is a series of curves defined by 2D points.

    They are usually stored as simple CSV files.
    """


@drawing.command()
@click.argument('symbol', required=False)
def list(symbol):
    """
    List all drawings in a TexnoMagic symbol.

    By default, tries to detect symbol from current directory.

    Select a specific symbol by passing ALPHABET/SYMBOL string.
    """
    s = cli_common.get_symbol_or_fail(symbol)
    s.load()
    cli_common.print_drawings(s.drawings)


@drawing.command()
@click.argument('drawing', nargs=-1, required=True)
def show(drawing):
    """
    Show information about TexnoMagic drawing(s).

    Select one or more drawing CSV files as arguments.

    Use `texnomagic drawing list` to work on symbols instead of files.
    """
    drawings = cli_common.parse_drawings_arg(drawing)
    cli_common.print_drawings(drawings)


TEXNOMAGIC_CLI_COMMANDS = [drawing]
