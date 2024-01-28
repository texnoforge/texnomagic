import click
from rich.syntax import Syntax

from texnomagic import common
from texnomagic.console import console
from texnomagic import lang


@click.group(name='spell')
@click.help_option('-h', '--help', help='Show command help.')
def spell():
    """
    Parse and work with TexnoMagic Spells.
    """


@spell.command()
@click.argument('spell', nargs=-1, required=True)
@click.option('-f', '--format',
              default=common.DUMP_FORMAT_DEFAULT, show_default=True,
              type=click.Choice(common.DUMP_FORMATS),
              help="Output format")
@click.help_option('-h', '--help', help='Show command help.')
def parse(spell, format):
    """
    Parse a TexnoMagic Spell string.
    """
    text = " ".join(spell)
    txlang = lang.TexnoMagicLanguage()
    try:
        out = txlang.parse(text)
    except Exception as e:
        console.print("[bold red]Spell Parse Error[/]: %s" % e)
        return 42

    common.pretty_print(out, format=format)


@spell.command()
@click.option('--ln/--no-ln', default=True, show_default=True,
              help="Show line numbers.")
@click.help_option('-h', '--help', help='Show command help.')
def grammar(ln):
    """
    Show TexnoMagic Spell Grammar.

    The output is PEG grammar as used by Parsimonious python module.
    """
    syntax = Syntax(lang.TEXNOMAGIC_GRAMMAR, 'peg', line_numbers=ln)
    console.print(syntax)


TEXNOMAGIC_CLI_COMMANDS = [spell]
