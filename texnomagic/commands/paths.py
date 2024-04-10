import click
import os

from texnomagic.console import console
from texnomagic import common
from texnomagic import ex


@click.command()
@click.option('-a', '--abcs',
              help="Only show specified alphabets path and exit.")
@click.option('-m', '--mkdir', is_flag=True,
              help="Create alphabets dirs including parents. Use -a to select.")
@click.option('-o', '--open', is_flag=True,
              help="Open path(s) in system app (file explorer). Use -a to select.")
@click.help_option('-h', '--help', help='Show command help.')
def paths(abcs, mkdir, open):
    """
    Show TexnoMagic file paths.
    """
    if abcs:
        path = common.ALPHABETS_PATHS.get(abcs)
        if not path:
            console.print(f"[red]Invalid alphabets path tag: {abcs}[/]")
            tags = ', '.join(common.ALPHABETS_PATHS)
            console.print(f"\nAvailable alphabet paths: {tags}")
            raise ex.InvalidInput()

        if mkdir:
            path.mkdir(parents=True, exist_ok=True)
        print(path)
        if open:
            os.startfile(path)
        return

    for tag, path in common.ALPHABETS_PATHS.items():
        if mkdir:
            path.mkdir(parents=True, exist_ok=True)
        if path.exists():
            exstr = "[green]exists[/]"
            if open:
                os.startfile(path)
        else:
            exstr = "[yellow]doesn't exist[/]"
        console.print(f"[bold]{tag}[/] alphabets: [bold]{path}[/] ({exstr})")


TEXNOMAGIC_CLI_COMMANDS = [paths]
