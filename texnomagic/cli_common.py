from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic.abc import find_alphabet_at_path
from texnomagic.symbol import find_symbol_at_path
from texnomagic.console import console
from texnomagic import common
from texnomagic import ex


OUTPUT_FORMATS = ['text'] + common.DUMP_FORMATS
OUTPUT_FORMAT_DEFAULT = 'text'


def get_alphabet_of_fail(abc):
    alphabet = None
    if abc:
        abcs = TexnoMagicAlphabets()
        abcs.load()
        alphabet = abcs.get_alphabet(abc)
        if not alphabet:
            console.print(f"[yellow]TexnoMagic alphabet not found[/]: [cyan]{abc}[/]")
            raise ex.AlphabetNotFound(abc)
    else:
        alphabet = find_alphabet_at_path()
        if not alphabet:
            console.print("[yellow]No TexnoMagic alphabet found at current path.[/]\n")
            print("You can:\n")
            print("- run from a (sub-)directory of a TexnoMagic alphabet")
            print("- select TexnoMagic alphabet by name using an argument")
            raise ex.AlphabetNotFound()

    return alphabet


def get_symbol_or_fail(symbol):
    _symbol = None
    if symbol:
        abc_name, _, symbol_name = symbol.rpartition('/')
        if not abc_name:
            console.print(f"[red]Inavlid symbol spec[/]: [green]{symbol}[/]")
            console.print("\nPlease use ALPHABET/SYMBOL format.")
            raise ex.InvalidInput(symbol)
        _abc = get_alphabet_of_fail(abc_name)
        _symbol = _abc.get_symbol(symbol_name)
        if not _symbol:
            console.print(f"[yellow]TexnoMagic symbol not found[/]: [green]{symbol}[/]")
            raise ex.SymbolNotFound(symbol)
    else:
        _symbol = find_symbol_at_path()
        if not _symbol:
            console.print("[yellow]No TexnoMagic symbol found at current path.[/]\n")
            print("You can:\n")
            print("- run from a (sub-)directory of a TexnoMagic symbol")
            print("- select TexnoMagic symbol by name passing ALPHABET/SYMBOL argument")
            raise ex.SymbolNotFound()
    return _symbol
