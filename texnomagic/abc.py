import json
import os
from pathlib import Path
import random
import shutil

import numpy as np

from texnomagic import common
from texnomagic.symbol import TexnoMagicSymbol


class TexnoMagicAlphabet:
    def __init__(self, path=None, name=None):
        self.path = path
        self.name = name
        self._symbols = None

    @property
    def info_path(self):
        return self.path / 'texno_alphabet.json'

    @property
    def symbols_path(self):
        return self.path / 'symbols'

    @property
    def symbols(self):
        if self._symbols is None:
            self.load_symbols()
        return self._symbols

    def load(self, path=None):
        if path:
            self.path = path

        assert self.path
        info = json.load(self.info_path.open())

        name = info.get('name')
        if not name:
            name = self.path.name
        self.name = name

        return self

    def load_symbols(self):
        self._symbols = []
        for symbol_info_path in self.symbols_path.glob('*/texno_symbol.json'):
            symbol = TexnoMagicSymbol()
            symbol.load(symbol_info_path.parent)
            self._symbols.append(symbol)
        self.sort_symbols()

    def sort_symbols(self):
        if not self._symbols:
            return
        known = []
        for core_symbol in common.CORE_SYMBOLS_ORDER:
            for symbol in self._symbols:
                if symbol.meaning == core_symbol:
                    known.append(symbol)
                    self._symbols.remove(symbol)
                    break
        self._symbols = known + self._symbols

    def save(self):
        os.makedirs(self.path, exist_ok=True)
        info = {
            'name': self.name,
        }
        return json.dump(info, self.info_path.open('w'))

    def save_new_symbol(self, symbol):
        assert symbol.name

        if self._symbols is None:
            self.load_symbols()

        symbol.path = self.symbols_path / common.name2fn(symbol.name)
        symbol.save()
        return self._symbols.insert(0, symbol)

    def export(self, out_path=None):
        """
        export alphabet into a zipfile
        """
        if not out_path:
            out_path = common.EXPORT_PATH

        ar_fn = self.path.name
        out_fn = out_path / ar_fn
        return shutil.make_archive(
            out_fn, 'zip',
            root_dir=self.path.parent,
            base_dir=self.path.name,
        )

    def train_models(self, all=False):
        """
        train symbol models with available drawings

        train only missing models by default, use all to (re-)train all
        """
        new, fail, old = [], [], []
        for symbol in self.symbols:
            if all or not symbol.model.ready:
                if symbol.model.train_symbol(symbol):
                    symbol.model.save()
                    new.append(symbol)
                else:
                    fail.append(symbol)
            else:
                old.append(symbol)
        return new, fail, old

    def calibrate(self):
        self.train_models(all=True)

    def scores(self, drawing):
        """
        recognize drawing using all symbol models

        return a list of (symbol, score) tuples ordered by score desc
        """
        s = [(symbol, symbol.model.score(drawing)) for symbol in self.symbols]
        s = sorted(s, key=lambda x: x[1], reverse=True)
        return s

    def recognize(self, drawing):
        s = self.scores(drawing)
        if not s:
            return None, -1
        _symbol, score = s[0]
        if score < common.MIN_SCORE:
            return None, score
        return s

    def check(self):
        """
        check alphabet for problems
        """
        warns = dict()

        def log_warn(key, val=1.0):
            if key in warns:
                n, v = warns[key]
                warns[key] = (n + 1, (v * n + val) / (n + 1))
            else:
                warns[key] = (1, val)

        for symbol in self.symbols:
            if not symbol.model.ready:
                log_warn(('warn', 'missing_model', symbol), -1)
            for drawing in symbol.drawings:
                scores = self.scores(drawing)
                rsymbol, rscore = scores[0]
                if rsymbol.meaning != symbol.meaning:
                    log_warn(('error', 'wrong_symbol', symbol, rsymbol), rscore)
                    prob = 'wrong_symbol'

                for rsy, rsc in scores[1:]:
                    # check scores for other symbols too
                    if rsc > 0.6:
                        lvl = 'warn'
                        if rsc > 0.8:
                            lvl = 'error'
                        log_warn((lvl,'high_score', symbol, rsy), rsc)

        results = {}
        for (level, prob, *args), (n, score) in warns.items():
            if prob == 'high_score':
                msg = "%s drawing got high score in %s: %s" % (args[0].meaning, args[1].meaning, score)
            elif prob == 'missing_model':
                msg = "%s symbol is missing model" % args[0].meaning
            else:
                msg = "%s drawing recognized as %s: %s" % (args[0].meaning, args[1].meaning, score)
            if n > 1:
                msg += "  (x%s)" % n
            if level not in results:
                results[level] = []
            results[level].append(msg)

        return results

    def get_symbol_by_name(self, name):
        for s in self.symbols:
            if s.name == name:
                return s
        return None

    def random_symbol(self, exclude=None):
        if exclude:
            symbols = [s for s in self.symbols if s != exclude]
        else:
            symbols = self.symbols
        if len(symbols) < 1:
            return None
        return random.choice(symbols)

    def stats(self, full=False):
        if full:
            return "%s: %s symbols @ %s" % (self.name, len(self.symbols), self.path)
        return "%s: %s symbols" % (self.name, len(self.symbols))

    def __repr__(self):
        return "<TexnoMagicAlphabet: %s>" % self.stats()
