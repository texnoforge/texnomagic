"""
TexnoMagic CLI
"""
import json
import sys

import click

from texnomagic import __version__
from texnomagic import lang
from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic import mods
from texnomagic import server as server_


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
    pass


@cli.command()
@click.argument('abc', nargs=-1)
@click.option('-n', '--names', is_flag=True,
              help="List names only (no details).")
@click.option('-f', '--full', is_flag=True,
              help="List everything including symbols.")
def list_abcs(abc, names, full):
    """
    List all/selected TexnoMagic alphabets.
    """
    abcs = TexnoMagicAlphabets()
    abcs.load()

    for tag, _abcs in abcs.abcs.items():
        if not names:
            print("%s %s:" % (len(_abcs), tag))
        for abc_ in _abcs:
            if abc and abc_.name not in abc:
                continue
            if names:
                print(abc_.name)
            else:
                print("%s" % abc_.stats(full=full))
            if full:
                for symbol in abc_.symbols:
                    if names:
                        print("  %s" % symbol.name)
                    else:
                        print("  %s" % symbol.stats(full=True))

    return 0


@cli.command()
@click.argument('abc', nargs=-1)
def check_abcs(abc):
    """
    Check all/selected alphabets for issues.
    """
    all_abcs = TexnoMagicAlphabets()
    all_abcs.load()

    for tag, _abcs in all_abcs.abcs.items():
        for abc_ in _abcs:
            if abc and abc_.name not in abc:
                continue
            print("CHECK %s" % abc_.stats(full=True))
            r = abc_.check()
            for level, msgs in sorted(r.items()):
                for msg in msgs:
                    print("%s: %s" % (level.upper(), msg))
    return 0


@cli.command()
@click.argument('abc', nargs=-1)
@click.option('-a', '--all', is_flag=True,
              help="Re-train all models. (default: only missing)")
def train_abcs(abc, all):
    """
    Train (missing) models for all/selected alphabets.
    """
    all_abcs = TexnoMagicAlphabets()
    all_abcs.load()

    first = True
    for tag, _abcs in all_abcs.abcs.items():
        for abc_ in _abcs:
            if abc and abc_.name not in abc:
                continue
            if first:
                first = False
            else:
                print()
            print("%s" % abc_.stats(full=True))
            new, fail, old = abc_.train_models(all=all)
            if new:
                print("TRAIN %s symbol models: %s" % (len(new), ", ".join([s.meaning for s in new])))
            if fail:
                print("FAIL %s symbol models: %s" % (len(fail), ", ".join([s.meaning for s in fail])))
            if old:
                print("ORIG %s symbol models: %s" % (len(old), ", ".join([s.meaning for s in old])))

    return 0


@cli.command()
@click.argument('spell', nargs=-1, required=True)
def spell(spell):
    """
    Parse TexnoMagic spell.
    """
    text = " ".join(spell)
    txlang = lang.TexnoMagicLanguage()
    try:
        out = txlang.parse(text)
    except Exception as e:
        print("parse error: %s" % e)
        return 42

    try:
        print(json.dumps(out, indent=4, sort_keys=False))
    except TypeError:
        print(out)
    return 0


@cli.command()
@click.argument('port', type=int, nargs=1, default=server_.DEFAULT_PORT)
def server(port):
    """
    Start TexnoMagic TCP server on PORT.
    """
    server_.serve(port=port)


@cli.command()
@click.argument('abc', nargs=1, required=True)
def flip_y(abc):
    """
    Flip Y axis for all symbols in alphabet.
    """
    abcs = TexnoMagicAlphabets()
    abcs.load()
    abc_ = abcs.get_abc_by_name(abc)
    if not abc_:
        print("alphabet not found: %s" % abc)
        return 20
    print(abc_)
    for symbol in abc_.symbols:
        print(symbol)
        for drawing in symbol.drawings:
            drawing.load_curves()
            drawing.flip_y_axis()
            drawing.save()


@cli.command()
def list_mods():
    """
    List online Words of Power mods from wop.mod.io.
    """
    for m in mods.get_online_mods():
        print("%s: %s  @ %s" % (m.name_id, m.name, m.profile_url))


@cli.command()
@click.argument('mod', nargs=-1)
@click.option('-a', '--all', is_flag=True,
              help="Download ALL mods. (default: only selected)")
def download_mods(mod, all):
    """
    Download Words of Power mods from wop.mod.io.
    """
    def do_dl(mod_):
        print("DOWNLOAD MOD: %s" % mod_)
        mod_.download()

    all_mods = mods.get_online_mods()
    if all:
        # all mods
        for mod in all_mods:
            do_dl(mod)
        return

    # selected mods
    for mod_id in mod:
        for m in all_mods:
            if all or m.name_id == mod_id or m.name == mod_id:
                do_dl(m)
                break
        else:
            print("mod not found - skipping: %s" % mod_id)


def main():
    cli()


if __name__ == '__main__':
    main()
