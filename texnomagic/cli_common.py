from pathlib import Path

from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic.abc import find_alphabet_at_path
from texnomagic.symbol import find_symbol_at_path
from texnomagic.drawing import TexnoMagicDrawing
from texnomagic import console
from texnomagic import common
from texnomagic import ex


OUTPUT_FORMATS = ['text'] + common.DUMP_FORMATS
OUTPUT_FORMAT_DEFAULT = 'text'


def get_alphabet_or_fail(abc, auto_load=True):
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

    if auto_load:
        alphabet.load()

    return alphabet


def get_symbol_or_fail(symbol, auto_load=True):
    _symbol = None
    if symbol:
        abc_name, _, symbol_name = symbol.rpartition('/')
        if not abc_name:
            console.print(f"[red]Inavlid symbol spec[/]: [green]{symbol}[/]")
            console.print("\nPlease use ALPHABET/SYMBOL format.")
            raise ex.InvalidInput(symbol)
        _abc = get_alphabet_or_fail(abc_name)
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

    if auto_load:
        _symbol.load()

    return _symbol


def print_drawings(drawings, stats=True):
    n_points = 0
    n_curves = 0
    n_bytes = 0
    n = len(drawings)

    for drawing in drawings:
        n_points += len(drawing.points)
        n_curves += len(drawing.curves)
        n_bytes += drawing.file_size
        drawing.load()
        console.print(drawing.pretty())

    if not stats or n <= 0:
        return

    avg_points = n_points / float(n)
    avg_curves = n_curves / float(n)
    avg_bytes = n_bytes / float(n)

    print()
    console.print("[bold white]average[/]: %.1f points, "
                  "%.1f curves, %d kB"
                  % (avg_points, avg_curves, avg_bytes / 1024.0))
    print()
    console.print("[bold white]total[/]: %.1f points, "
                  "%.1f curves, %d kB, %d drawings"
                  % (n_points, n_curves, n_bytes / 1024.0, n))


def parse_drawings_arg(drawings):
    r = []
    for d in drawings:
        drawing_path = Path(d)
        if not drawing_path.exists():
            console.log(f"[red]Drawing file not found[/]: [white]{d}[/]")
            raise ex.DrawingNotFound(d)
        dr = TexnoMagicDrawing(drawing_path)
        r.append(dr)
    return r
