import click

from texnomagic import common
from texnomagic import mods
from texnomagic.console import console
from texnomagic import cli_common


@click.group()
@click.help_option('-h', '--help', help='Show command help.')
def mod():
    """
    Manage Words of Power mods.
    """


@mod.command()
@click.help_option('-h', '--help', help='Show command help.')
@click.option('-f', '--format',
              default=cli_common.OUTPUT_FORMAT_DEFAULT, show_default=True,
              type=click.Choice(cli_common.OUTPUT_FORMATS),
              help="Select output format.")
def list(format):
    """
    List online Words of Power mods from wop.mod.io.
    """
    mods_ = mods.get_online_mods()
    if format == 'text':
        for m in mods_:
            console.print(f"[bold cyan]{m.name}[/]: {m.profile_url}")
    else:
        mod_dict = {m.name_id: m.as_dict() for m in mods_}
        common.pretty_print(mod_dict, format=format)


@mod.command()
@click.argument('mod', nargs=-1)
@click.option('-a', '--all', is_flag=True,
              help="Download ALL mods.  [default: only selected]")
def download(mod, all):
    """
    Download Words of Power mods from wop.mod.io.
    """
    def do_dl(mod_):
        console.log(f"[yellow]DOWNLOADING MOD[/]: [bold cyan]{mod_.name}[/] from {mod_.profile_url}")
        mod_.download()
        console.log(f"[green]DOWNLOADED MOD[/]: [bold cyan]{mod_.name}[/] from {mod_.profile_url}")

    all_mods = mods.get_online_mods()
    if all:
        # all mods
        for mod in all_mods:
            do_dl(mod)
        return

    # selected mods
    for mod_id in mod:
        for m in all_mods:
            if all or m.name_id == mod_id or m.name == mod_id:
                do_dl(m)
                break
        else:
            console.log(f"[red]Mod not found[/] - [yellow]skipping[/]: {mod_id}")


TEXNOMAGIC_CLI_COMMANDS = [mod]
