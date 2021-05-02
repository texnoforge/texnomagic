
import glob
from pathlib import Path

from texnomagic.abc import TexnoMagicAlphabet
from texnomagic import common


class TexnoMagicAlphabets:
    def __init__(self, paths=None):
        self.paths = paths or common.ALPHABETS_PATHS
        self.abcs = {}

    def load(self):
        self.abcs = {}
        for tag, path in self.paths.items():
            self.abcs[tag] = get_alphabets(path)

    def get_abc_by_name(self, name):
        for _, abcs in self.abcs.items():
            for abc in abcs:
                if abc.name == name:
                    return abc
        return None

    def save_new_alphabet(self, abc, tag='user'):
        assert abc.name
        abc.path = self.paths[tag] / common.name2fn(abc.name)
        abc.save()
        self.abcs[tag].insert(0, abc)
        return abc

    def stats(self):
        stats = []
        for tag, abcs in self.abcs.items():
            stats.append('%d %s' % (len(abcs), tag))

        if not stats:
            stats = ['no alphabets found :(']

        return ", ".join(stats)

    def __repr__(self):
        return "<TexnoMagicAlphabets: %s>" % self.stats()


def get_alphabets(paths=None):
    paths = paths or common.ALPHABETS_PATHS
    abcs = []
    for abc_info_path in paths.glob('*/texno_alphabet.json'):
        abc = TexnoMagicAlphabet()
        abc.load(abc_info_path.parent)
        abcs.append(abc)
    return abcs
