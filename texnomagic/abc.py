import json
import os
from pathlib import Path
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

    def calibrate(self):
        """
        calibrate symbol models in this alphabet
        """
        for symbol in self.symbols:
            if not symbol.model:
                if symbol.train_model_from_drawings():
                    symbol.save()
                print("trained missing model for %s", symbol.name)
            if not symbol.model:
                print("skipping missing model for %s", symbol.name)
                continue

            print("calibrating %s symbol model", symbol.name)
            for test_symbol in self.symbols:
                if symbol == test_symbol:
                    continue
                if not test_symbol.drawings:
                    continue

    def recognize(self, drawing):
        best_symbol = None
        best_score = -999999999999999
        if len(drawing.points) < 1:
            return None, best_score

        for symbol in self.symbols:
            score = symbol.model.score(drawing)
            # DEBUG - remove
            print("  %s: %s" % (symbol.name, score))
            if score > best_score:
                best_score = score
                best_symbol = symbol
        return best_symbol, best_score

    @property
    def symbols(self):
        if self._symbols is None:
            self.load_symbols()
        return self._symbols

    def __repr__(self):
        return "<TexnoMagicAlphabet: %s: %s symbols>" % (self.name, len(self.symbols))
