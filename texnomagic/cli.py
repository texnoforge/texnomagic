"""
TexnoMagic CLI
"""
import logging
import os
import pkgutil
import sys

import click

from texnomagic import __version__
from texnomagic import commands
from texnomagic import ex
from texnomagic import console as console_mod


log = logging.getLogger(__name__)


COLOR_SYSTEMS = ['auto', 'none', 'standard', '256', 'truecolor', 'windows']
CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__, message='%(version)s',
                      help="Show TexnoMagic version and exit.")
@click.option('-C', '--color', default='auto', show_default=True,
              type=click.Choice(COLOR_SYSTEMS),
              help="Set color mode.")
def cli(color):
    """
    TexnoMagic CLI
    """
    if color == 'none':
        console_mod.console = console_mod.Console(color_system=None)
    elif color != 'auto':
        console_mod.console = console_mod.Console(color_system=color)


def __load_commands():
    """
    load available texnomagic commands

    should only be called once on module load
    """
    pkgpath = os.path.dirname(commands.__file__)
    for _, modname, _ in pkgutil.iter_modules([pkgpath]):
        modpath = "texnomagic.commands.%s" % (modname)
        mod = __import__(modpath, fromlist=[''])
        cmds = getattr(mod, 'TEXNOMAGIC_CLI_COMMANDS', None)
        if not cmds:
            log.warning('command module with no CLI commands: %s', modpath)
            continue
        for cmd in cmds:
            cli.add_command(cmd)


__load_commands()


def main():
    try:
        cli()
    except ex.TexnoMagicException as e:
        sys.exit(e.returncode)



if __name__ == '__main__':
    main()
