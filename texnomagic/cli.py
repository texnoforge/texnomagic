import argparse
import json
import sys


from texnomagic import __version__
from texnomagic import lang
from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic import mods
from texnomagic import server


def cli(*cargs):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='command to run', dest='command')
    parser.add_argument('--version', action='version', version='TexnoMagic %s' % __version__)

    list_parser = subparsers.add_parser(
        "list-abcs", help="list available alphabets")
    list_parser.add_argument('abc', nargs='*',
        help="alphabets to list (default: all)")
    list_parser.add_argument('--names', action='store_true',
        help="list names only without origins")
    list_parser.add_argument('--full', action='store_true',
        help="list everything")

    check_parser = subparsers.add_parser(
        "check-abcs", help="check alphabets for issues")
    check_parser.add_argument('abc', nargs='*',
        help="alphabets to check (default: all)")

    train_parser = subparsers.add_parser(
        "train-abcs", help="train (missing) models for selected alphabets")
    train_parser.add_argument('abc', nargs='*',
        help="alphabets to train (default: all)")
    train_parser.add_argument('--all', action='store_true',
        help="re-train all models (default: only missing)")

    list_parser = subparsers.add_parser(
        "list-mods", help="list available mods from wop.mod.io")

    dl_parser = subparsers.add_parser(
        "download-mods", help="download mod(s) from wop.mod.io")
    dl_parser.add_argument('mod', nargs='+',
        help="Words of Power mod to download")

    spell_parser = subparsers.add_parser(
        "spell", help="parse TexnoMagic spell")
    spell_parser.add_argument('text', nargs='+',
        help="TexnoMagic spell to parse")

    server_parser = subparsers.add_parser(
        "server", help="start TexnoMagic TCP server")
    server_parser.add_argument('port', nargs='?', type=int, default=server.DEFAULT_PORT,
        help="TCP port number to run on (default: %s)" % server.DEFAULT_PORT)

    flip_parser = subparsers.add_parser(
        "flip-y", help="flip Y axis for all symbols in alphabet")
    flip_parser.add_argument('abc',
        help="alphabet to flip Y axis")

    if len(cargs) < 1:
        parser.print_usage()
        return 1

    args = parser.parse_args(cargs)
    cmd = args.command.replace('-', '_')
    fun = 'command_%s' % cmd
    return globals()[fun](**vars(args))


def command_list_abcs(**kwargs):
    abcs = TexnoMagicAlphabets()
    abcs.load()
    only_abcs = kwargs.get('abc')
    names = kwargs.get('names')
    full = kwargs.get('full')

    for tag, _abcs in abcs.abcs.items():
        if not names:
            print("%s %s:" % (len(_abcs), tag))
        for abc in _abcs:
            if only_abcs and abc.name not in only_abcs:
                continue
            if names:
                print(abc.name)
            else:
                print("%s" % abc.stats(full=full))
            if full:
                for symbol in abc.symbols:
                    if names:
                        print("  %s" % symbol.name)
                    else:
                        print("  %s" % symbol.stats(full=True))

    return 0


def command_check_abcs(**kwargs):
    all_abcs = TexnoMagicAlphabets()
    all_abcs.load()
    only_abcs = kwargs.get('abc')

    for tag, _abcs in all_abcs.abcs.items():
        for abc in _abcs:
            if only_abcs and abc.name not in only_abcs:
                continue
            print("CHECK %s" % abc.stats(full=True))
            r = abc.check()
            for level, msgs in sorted(r.items()):
                for msg in msgs:
                    print("%s: %s" % (level.upper(), msg))
    return 0


def command_train_abcs(**kwargs):
    all_abcs = TexnoMagicAlphabets()
    all_abcs.load()
    only_abcs = kwargs.get('abc')
    retrain = kwargs.get('retrain')

    first = True
    for tag, _abcs in all_abcs.abcs.items():
        for abc in _abcs:
            if only_abcs and abc.name not in only_abcs:
                continue
            if first:
                first = False
            else:
                print()
            print("%s" % abc.stats(full=True))
            new, fail, old = abc.train_models(all=retrain)
            if new:
                print("TRAIN %s symbol models: %s" % (len(new), ", ".join([s.meaning for s in new])))
            if fail:
                print("FAIL %s symbol models: %s" % (len(fail), ", ".join([s.meaning for s in fail])))
            if old:
                print("ORIG %s symbol models: %s" % (len(old), ", ".join([s.meaning for s in old])))

    return 0


def command_spell(**kwargs):
    texts = kwargs.get('text', [])
    text = " ".join(texts)
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


def command_server(**kwargs):
    port = kwargs.get('port', server.DEFAULT_PORT)
    server.serve(port=port)


def command_flip_y(**kwargs):
    abc_name = kwargs.get('abc')
    abcs = TexnoMagicAlphabets()
    abcs.load()
    abc = abcs.get_abc_by_name(abc_name)
    if not abc:
        print("alphabet not found: %s" % abc_name)
        return 20
    print(abc)
    for symbol in abc.symbols:
        print(symbol)
        for drawing in symbol.drawings:
            drawing.load_curves()
            drawing.flip_y_axis()
            drawing.save()


def command_list_mods(**_):
    for m in mods.get_online_mods():
        print("%s: %s  @ %s" % (m.name_id, m.name, m.profile_url))


def command_download_mods(**kwargs):
    all_mods = mods.get_online_mods()
    for mod_id in kwargs.get('mod', []):
        for m in all_mods:
            if m.name_id == mod_id or m.name == mod_id:
                print("DOWNLOAD MOD: %s" % m)
                m.download()
                break
        else:
            print("mod not found - skipping: %s" % mod_id)


def main():
    cargs = sys.argv[1:]
    sys.exit(cli(*cargs))


if __name__ == '__main__':
    main()
