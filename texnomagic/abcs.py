
import glob
from pathlib import Path

from texnomagic.abc import TexnoMagicAlphabet
from texnomagic import common



class TexnoMagicAlphabets:
    def __init__(self, paths):
        self.paths = paths or {}
        self.abcs = {}

    def load(self):
        self.abcs = {}
        for tag, path in self.paths.items():
            self.abcs[tag] = get_alphabets(path)

    def save_new_alphabet(self, abc, tag='user'):
        assert abc.name
        abc.base_path = self.paths[tag] / common.name2fn(abc.name)
        abc.save()
        self.abcs[tag].insert(0, abc)
        return abc

    def __repr__(self):
        stats = []
        for tag, abcs in self.abcs.items():
            stats.append('%d %s' % (len(abcs), tag))

        if not stats:
            stats = ['no alphabets found :(']

        return "<TexnoMagicAlphabets: %s>" % ", ".join(stats)


def get_alphabets(base_path):
    abcs = []
    for abc_info_path in base_path.glob('*/texno_alphabet.json'):
        abc = TexnoMagicAlphabet()
        abc.load(abc_info_path.parent)
        abcs.append(abc)
    return abcs
