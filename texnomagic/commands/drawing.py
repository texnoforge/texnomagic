import click

from texnomagic import abc as abc_mod
from texnomagic import cli_common
from texnomagic.console import console
from texnomagic import ex


@click.group()
@click.help_option('-h', '--help', help='Show command help.')
def drawing():
    """
    Manage TexnoMagic drawings.

    A drawings is a series of curves defined by 2D points.

    They are usually stored as simple CSV files.
    """


@drawing.command()
@click.argument('symbol', required=False)
def list(symbol):
    """
    List all drawings in a TexnoMagic symbol.

    By default, tries to detect symbol from current directory.

    Select a specific symbol by passing ALPHABET/SYMBOL string.
    """
    s = cli_common.get_symbol_or_fail(symbol)
    s.load()
    cli_common.print_drawings(s.drawings)


@drawing.command()
@click.argument('drawing', nargs=-1, required=True)
def show(drawing):
    """
    Show information about TexnoMagic drawing(s).

    Select one or more drawing CSV files as arguments.

    Use `texnomagic drawing list` to work on symbols instead of files.
    """
    drawings = cli_common.parse_drawings_arg(drawing)
    cli_common.print_drawings(drawings)


@drawing.command()
@click.argument('drawing', nargs=-1, required=True)
def normalize(drawing):
    """
    Normalize TexnoMagic drawing(s).
    """
    drawings = cli_common.parse_drawings_arg(drawing)
    for d in drawings:
        if d.points.any():
            console.print(f"[green]NORMALIZING[/] drawing: {d.pretty()}")
            d.normalize()
            d.save()


@drawing.command()
@click.argument('drawing', nargs=-1, required=True)
@click.option('-a', '--abc',
              help="Recognize within selected TexnoMagic alphabet.")
@click.option('-s', '--symbol',
              help="Recognize against selected TexnoMagic symbol.")
@click.option('-m', '--min-score', type=float, default=float('-inf'),
              help="Only show results above this score.")
@click.option('-M', '--max-score', type=float, default=float('inf'),
              help="Only show results below this score.")
@click.option('-n', '--max-drawings', type=int, default=None,
              help="Only show at most this many resulting drawings.")
@click.option('-N', '--max-symbols', type=int, default=None,
              help="Only show at most this many resulting symbols. (in alphabet mode)")
@click.option('-r', '--reverse-drawings', is_flag=True,
              help="Reverse sorting of drawings.  [default: score descending]")
@click.option('-R', '--reverse-symbols', is_flag=True,
              help="Reverse sorting of symbols. (in alphabet mode)  [default: score descending]")
@click.option('--norm/--no-norm', default=True, show_default=True,
              help='Normalize drawing before recognition.')
@click.option('--rating/--no-rating', default=True, show_default=True,
              help="Show written rating alongside score.")
def recognize(drawing, abc, symbol, min_score, max_score, max_drawings, max_symbols, reverse_drawings, reverse_symbols, norm, rating):
    """
    Recognize selected drawings.

    Select

    a) TexnoMagic alphabet: --abc ALPHABET to match against all its symbols.

    b) TexnoMagic symbol: --symbol ALPHABET/SYMBOL to match against.

    c) nothing to use TexnoMagic alphabet found in current path.
    """
    drawings = cli_common.parse_drawings_arg(drawing)

    rabc = None
    rsymbol = None

    if not abc and not symbol:
        rabc = abc_mod.find_alphabet_at_path()
        if not rabc:
            console.print("[yellow]No TexnoMagic alphabet found at current path.[/]\n")
            print("You can:\n")
            print("- run from a (sub-)directory of a TexnoMagic alphabet")
            print("- select TexnoMagic alphabet using --abc ALPHABET")
            print("- select TexnoMagic symbol using --symbol ALPHABET/SYMBOL")
            raise ex.AlphabetNotFound()
        rabc.load()
    elif abc:
        rabc = cli_common.get_alphabet_of_fail(abc)
    elif symbol:
        rsymbol = cli_common.get_symbol_or_fail(symbol)

    if norm:
        for d in drawings:
            d.normalize()

    msg_base = f"[green]RECOGNIZING[/] {len(drawings)} drawings"
    if rabc:
        # Alphabet mode
        scores = []
        for d in drawings:
            symbol_scores = []
            # filter within <min_score; max_score>
            for s, score in rabc.scores(d, reverse=not reverse_symbols):
                if score < min_score or score > max_score:
                    continue
                symbol_scores.append((s, score))
            # cut symbol results to max_symbols
            if max_symbols:
                symbol_scores = symbol_scores[:max_symbols]
            if symbol_scores:
                scores.append((d, symbol_scores))

        # sort by top score
        scores.sort(key=lambda s: s[1][0][1] if s[1] else 0.0, reverse=not reverse_drawings)
        # cut drawing results to max_drawings
        if max_drawings:
            scores = scores[:max_drawings]

        # print results
        for d, ss in scores:
            console.print(f"[bold]{d.path}[/]:")
            for symbol_, score in ss:
                console.print(f"  {symbol_.pretty()}: {score.pretty(rating=rating)}", highlight=False)
    else:
        # Symbol mode
        console.print(f"{msg_base} against [bold]symbol[/]: {rsymbol.pretty()}")
        scores = []
        # filter within <min_score; max_score>
        for d in drawings:
            score = rsymbol.model.score(d)
            if score < min_score or score > max_score:
                continue
            scores.append((d, score))
        # sort by score
        scores.sort(key=lambda s: s[1], reverse=not reverse_drawings)
        # cut drawing results to max_drawings
        if max_drawings:
            scores = scores[:max_drawings]

        # print results
        for d, score in scores:
            console.print(f"[bold]{d.path}[/]: {score.pretty(rating=rating)}", highlight=False)


TEXNOMAGIC_CLI_COMMANDS = [drawing]
