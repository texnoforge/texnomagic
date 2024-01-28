import click

from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic.console import console
from texnomagic import common
from texnomagic import cli_common


@click.group()
@click.help_option('-h', '--help', help='Show command help.')
def abc():
    """
    Manage TexnoMagic alphabets.
    """


@abc.command()
@click.argument('abc', required=False)
@click.option('-f', '--format',
              default=common.DUMP_FORMAT_DEFAULT, show_default=True,
              type=click.Choice(common.DUMP_FORMATS),
              help="Select output format.")
def show(abc, format):
    """
    Show details of a TexnoMagic alphabet.

    By default, tries to detect alphabet from current directory.
    """
    alphabet = cli_common.get_alphabet_of_fail(abc)
    alphabet.load()
    common.pretty_print(alphabet.as_dict(), format)


@abc.command()
@click.argument('abc', nargs=-1)
@click.option('-t', '--tag',
              default=[], show_default=True,
              multiple=True,
              help="Filter alphabets by tag(s).")
@click.option('-n', '--names', is_flag=True,
              help="List unique names only (no details).")
@click.option('-s', '--symbols', is_flag=True,
              help="List individual symbols as well.")
@click.option('-f', '--format',
              default=cli_common.OUTPUT_FORMAT_DEFAULT, show_default=True,
              type=click.Choice(cli_common.OUTPUT_FORMATS),
              help="Select output format.")
def list(abc, tag, names, symbols, format):
    """
    List all/selected TexnoMagic alphabets.
    """
    abcs = TexnoMagicAlphabets()
    abcs.load()

    # are we outputting data or text?
    data_out = not names and format != 'text'

    # first filter by tags and names
    ftags = {}
    for _tag, _abcs in abcs.abcs.items():
        fabcs = []
        for _abc in _abcs:
            if abc and _abc.name not in abc and _abc.handle not in abc:
                continue
            if tag and _tag not in tag:
                continue
            if data_out:
                fabcs.append(_abc.as_dict(symbols=symbols))
            else:
                fabcs.append(_abc)
        if fabcs:
            ftags[_tag] = fabcs

    # list the filtered alphabets

    if data_out:
        # render as data
        common.pretty_print(ftags, format)
        return

    if names:
        # only list unique names
        unames = set()
        for _tag, _abcs in ftags.items():
            for _abc in _abcs:
                unames.add(_abc.name)
        for name in sorted(unames):
            console.print(name)
        return

    # print in text format (default)
    for _tag, _abcs in ftags.items():
        tag_path = abcs.paths.get(_tag)
        console.print(f"# [white]{len(_abcs)}[/] [orange4]{_tag}[/] alphabets @ [white]{tag_path}[/]")
        for _abc in _abcs:
            console.print(_abc.pretty())
            if symbols:
                for symbol in _abc.symbols:
                    console.print(f'  {symbol.pretty()}')


@abc.command()
@click.argument('abc', required=False)
def check(abc):
    """
    Check alphabet for issues.
    """
    alphabet = cli_common.get_alphabet_of_fail(abc)
    alphabet.load()

    console.print(f"[green]CHECK[/] alphabet: {alphabet.pretty(path=True)}")
    r = alphabet.check()
    for level, msgs in sorted(r.items()):
        for msg in msgs:
            print("%s: %s" % (level.upper(), msg))
    return 0


@abc.command()
@click.argument('abc', required=False)
@click.option('-a', '--all', is_flag=True,
              help="Re-train all models. (default: only missing)")
def train(abc, all):
    """
    Train (missing) models for alphabet.
    """
    alphabet = cli_common.get_alphabet_of_fail(abc)
    alphabet.load()

    console.print(f"[green]TRAIN[/] alphabet models: {alphabet.pretty(path=True)}")
    new, fail, old = alphabet.train_models(all=all)
    if new:
        console.print("[green]TRAIN[/] %s symbol models: %s" % (len(new), ", ".join([s.meaning for s in new])))
    if fail:
        console.print("[red]FAIL[/] %s symbol models: %s" % (len(fail), ", ".join([s.meaning for s in fail])))
    if old:
        console.print("[cyan]ORIG[/] %s symbol models: %s" % (len(old), ", ".join([s.meaning for s in old])))


@abc.command()
@click.argument('abc', required=False)
def flip_y(abc):
    """
    Flip Y axis for all symbols in alphabet.
    """
    alphabet = cli_common.get_alphabet_of_fail(abc)
    alphabet.load()

    console.print(f"[yellow]FLIP Y[/] alphabet: {alphabet.pretty(path=True)}")
    for symbol in alphabet.symbols:
        console.print(f"[yellow]FLIP Y[/] symbol: {symbol.pretty()}")
        for drawing in symbol.drawings:
            drawing.load_curves()
            drawing.flip_y_axis()
            drawing.save()


TEXNOMAGIC_CLI_COMMANDS = [abc]
