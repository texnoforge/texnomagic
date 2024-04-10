import click
from rich.prompt import Prompt

from texnomagic import console
from texnomagic import common
from texnomagic import cli_common
from texnomagic import ex
from texnomagic.symbol import TexnoMagicSymbol


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
    if names and meanings:
        # name (meaning)
        out_list = [s.pretty() for s in alphabet.symbols]
    elif meanings:
        # list meanings only
        out_list = [s.meaning for s in alphabet.symbols]
    elif names:
        # names meanings only
        out_list = [s.name for s in alphabet.symbols]

    if out_list:
        for o in out_list:
            console.print(o)
        return

    # print in text format (default)
    console.print(f"# {len(alphabet.symbols)} symbols @ {alphabet.symbols_path}")
    for symbol in alphabet.symbols:
        console.print(symbol.pretty(drawings=True, images=True, model=True))


@symbol.command()
@click.argument('abc', required=False)
@click.option('-m', '--meaning',
              help="Symbol meaning. Should be lowercase english.")
@click.option('-n', '--name',
              help="Symbol name. Any string is fine.")
def new(abc, meaning, name):
    """
    Create a new TexnoMagic symbol.

    By default, tries to detect alphabet from current directory.

    Select a specific alphabet by passing its name or handle as argument.
    """
    alphabet = cli_common.get_alphabet_of_fail(abc)

    if not (meaning or name):
        meaning = Prompt.ask("Symbol Meaning (lowercase english)")
        name = Prompt.ask("Symbol Name (any string)")
        print()
        if not (meaning or name):
            console.print("[red]ERROR[/]: symbol meaning or name is required")
            raise ex.InvalidInput()

    if not name:
        name = meaning
    if not meaning:
        meaning = name
    meaning = common.name2handle(meaning)

    symbol = TexnoMagicSymbol(meaning=meaning, name=name)
    alphabet.save_new_symbol(symbol)
    console.print(f"SAVED NEW symbol {symbol.pretty(path=True)}")


@symbol.command()
@click.argument('symbol', required=False)
def normalize(symbol):
    """
    Normalize drawings of selected TexnoMagic symbol.
    """
    _symbol = cli_common.get_symbol_or_fail(symbol)
    console.print(f"[green]NORMALIZING[/] symbol: {_symbol.pretty(drawings=True)}")
    _symbol.normalize()


TEXNOMAGIC_CLI_COMMANDS = [symbol]
