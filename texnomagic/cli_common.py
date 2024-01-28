from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic.abc import find_alphabet_at_path
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
