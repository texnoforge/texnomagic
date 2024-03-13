from texnomagic import abc as abc_
from texnomagic import common


class TexnoMagicAlphabets:
    def __init__(self, paths=None):
        self.paths = paths or common.ALPHABETS_PATHS
        self._abcs = None

    @property
    def abcs(self):
        if self._abcs is None:
            self.load()
        return self._abcs

    def load(self):
        self._abcs = {}
        for tag, path in self.paths.items():
            self._abcs[tag] = get_alphabets(path)

    def get_alphabet(self, name):
        tag, _, abc_name = name.rpartition(':')
        for tag_, abcs in self.abcs.items():
            if tag and tag != tag_:
                continue
            for abc in abcs:
                if abc_name == abc.name or abc_name == abc.handle:
                    return abc
        return None

    def save_new_alphabet(self, abc, tag='user'):
        assert abc.name
        abc.path = self.paths[tag] / common.name2fn(abc.name)
        abc.save()
        self.abcs[tag].insert(0, abc)
        return abc

    def pretty(self):
        s = []
        for tag, abcs in self.abcs.items():
            s.append('%d %s' % (len(abcs), tag))
        if not s:
            s = ['no alphabets found :(']
        return ", ".join(s)

    def __repr__(self):
        return "<TexnoMagicAlphabets: %s>" % self.pretty()


def get_alphabets(paths=None):
    paths = paths or common.ALPHABETS_PATHS
    abcs = []
    for abc_info_path in paths.glob(f'*/{abc_.INFO_FILE}'):
        abc = abc_.TexnoMagicAlphabet()
        abc.load(abc_info_path.parent)
        abcs.append(abc)
    return abcs
