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


log = logging.getLogger(__name__)


CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__, message='%(version)s',
                      help="Show TexnoMagic version and exit.")
def cli():
    """
    TexnoMagic CLI
    """


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
