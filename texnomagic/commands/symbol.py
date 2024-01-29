import click

from texnomagic.console import console
from texnomagic import common
from texnomagic import cli_common


@click.group()
@click.help_option('-h', '--help', help='Show command help.')
def symbol():
    """
    Manage TexnoMagic symbols.
    """


@symbol.command()
@click.argument('symbol', required=False)
@click.option('-f', '--format',
              default=common.DUMP_FORMAT_DEFAULT, show_default=True,
              type=click.Choice(common.DUMP_FORMATS),
              help="Select output format.")
def show(symbol, format):
    """
    Show details of a TexnoMagic symbol.

    By default, tries to detect symbol from current directory.

    Select a specific symbol by passing ALPHABET/SYMBOL string.
    """
    _symbol = cli_common.get_symbol_or_fail(symbol)
    _symbol.load()
    common.pretty_print(_symbol.as_dict(), format)


@symbol.command()
@click.argument('abc', required=False)
@click.option('-n', '--names', is_flag=True,
              help="List names only (no details).")
@click.option('-m', '--meanings', is_flag=True,
              help="List meanings only (no details).")
@click.option('-f', '--format',
              default=cli_common.OUTPUT_FORMAT_DEFAULT, show_default=True,
              type=click.Choice(cli_common.OUTPUT_FORMATS),
              help="Select output format.")
def list(abc, names, meanings, format):
    """
    List all symbols in a TexnoMagic alphabet.

    By default, tries to detect alphabet from current directory.

    Select a specific alphabet by passing its name or handle as argument.
    """
    alphabet = cli_common.get_alphabet_of_fail(abc)
    alphabet.load()

    # are we outputting data or text?
    data_out = not names and not meanings and format != 'text'

    # list the filtered alphabets

    if data_out:
        # render as data
        data = {s.meaning: s.as_dict() for s in alphabet.symbols}
        common.pretty_print(data, format)
        return

    out_list = None
    if meanings:
        # list meanings only
        out_list = [s.meaning for s in alphabet.symbols]
    if names:
        # names meanings only
        out_list = [s.name for s in alphabet.symbols]

    if out_list:
        for o in out_list:
            print(o)
        return

    # print in text format (default)
    console.print(f"# {len(alphabet.symbols)} symbols @ {alphabet.symbols_path}")
    for symbol in alphabet.symbols:
        console.print(symbol.pretty(n_drawings=True, model=True))


TEXNOMAGIC_CLI_COMMANDS = [symbol]
