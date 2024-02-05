from pathlib import Path

import click

from texnomagic import common
from texnomagic import cli_common
from texnomagic import drawing as drawing_mod
from texnomagic.gui.drawing import show_drawings_gui


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
def info(drawing):
    """
    Show information about TexnoMagic drawing(s).

    Select one or more drawing CSV files as arguments.

    Use `texnomagic drawing list` to work on symbols instead of files.
    """
    drawings = cli_common.parse_drawings_arg(drawing)
    cli_common.print_drawings(drawings)


@drawing.command()
@click.argument('drawing', nargs=-1, required=True)
@click.option('-r', '--resolution',
              default=drawing_mod.RESOLUTION_DEFAULT, show_default=True,
              help="Set image resolution.")
@click.option('-w', '--line-width',
              default=drawing_mod.LINE_WIDTH_DEFAULT, show_default=True,
              help="Set relative drawing line width.")
@click.option('-m', '--margin',
              default=drawing_mod.MARGIN_DEFAULT, show_default=True,
              help="Set relative margin around the drawing.")
@click.option('-M', '--merge', is_flag=True,
              help="Merge all drawings in a single image.")
def show(drawing, resolution, line_width, margin, merge):
    """
    Display TexnoMagic drawing(s) in GUI.
jjkjjk
    Select one or more drawing CSV files as arguments.

    Use `texnomagic drawing export` to save as images (PNG, SVG).
    """
    drawings = cli_common.parse_drawings_arg(drawing)

    show_drawings_gui(drawings, merge=merge, resolution=resolution, margin=margin, line_width=line_width)


@drawing.command()
@click.argument('drawing', nargs=-1, required=True)
@click.option('-f', '--format',
              default=common.IMAGE_FORMAT_DEFAULT, show_default=True,
              type=click.Choice(common.IMAGE_FORMATS),
              help="Select output format.")
@click.option('-r', '--resolution',
              default=drawing_mod.RESOLUTION_DEFAULT, show_default=True,
              help="Set image resolution.")
@click.option('-w', '--line-width',
              default=drawing_mod.LINE_WIDTH_DEFAULT, show_default=True,
              help="Set relative drawing line width.")
@click.option('-m', '--margin',
              default=drawing_mod.MARGIN_DEFAULT, show_default=True,
              help="Set relative margin around the drawing.")
@click.option('-O', '--result-dir', type=Path,
              help=("Save results into specified dir"
                    "  [default: same as input]"))
def export(drawing, format, resolution, line_width, margin, result_dir=None):
    """
    Export TexnoMagic drawing(s) as SVG/PNG images.

    Select one or more drawing CSV files as arguments.

    Use `texnomagic drawing show` to view in GUI.
    """
    drawings = cli_common.parse_drawings_arg(drawing)

    if result_dir:
        result_dir.mkdir(parents=True, exist_ok=True)

    for d in drawings:
        new_name = f'{d.path.stem}.{format}'
        if result_dir:
            out_path = result_dir / new_name
        else:
            out_path = d.path.parent / new_name

        d.export(out_path=out_path, format=format, res=resolution, line_width=line_width, margin=margin)


TEXNOMAGIC_CLI_COMMANDS = [drawing]
