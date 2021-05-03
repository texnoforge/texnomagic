import argparse
import json
import sys


from texnomagic import __version__
from texnomagic import lang
from texnomagic.abcs import TexnoMagicAlphabets


def cli(*cargs):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='command', dest='command')
    parser.add_argument('--version', action='version', version='TexnoMagic %s' % __version__)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument('abc', nargs='*',
        help="alphabets to list (default: all)")
    list_parser.add_argument('--names', action='store_true',
        help="list names only without origins")
    list_parser.add_argument('--full', action='store_true',
        help="list everything")

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument('abc', nargs='*',
        help="alphabets to check (default: all)")

    train_parser = subparsers.add_parser("train")
    train_parser.add_argument('abc', nargs='*',
        help="alphabets to train (default: all)")
    train_parser.add_argument('--all', action='store_true',
        help="re-train all models (default: only missing)")

    spell_parser = subparsers.add_parser("spell")
    spell_parser.add_argument('text', nargs='+',
        help="TexnoMagic spell to parse")

    if len(cargs) < 1:
        parser.print_usage()
        return 1

    args = parser.parse_args(cargs)
    fun = 'command_%s' % args.command
    return globals()[fun](**vars(args))


def command_list(**kwargs):
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


def command_check(**kwargs):
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


def command_train(**kwargs):
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


def main():
    cargs = sys.argv[1:]
    sys.exit(cli(*cargs))


if __name__ == '__main__':
    main()
