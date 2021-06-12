import json
import numpy as np
import os
import random
import time

from texnomagic import common
from texnomagic.drawing import TexnoMagicDrawing
from texnomagic.model import TexnoMagicSymbolModel


class TexnoMagicSymbol:
    def __init__(self, path=None, name=None, meaning=None):
        self.path = path
        self.name = name
        self.meaning = meaning
        self._drawings = None
        self._model = None

    @property
    def info_path(self):
        return self.path / 'texno_symbol.json'

    @property
    def drawings_path(self):
        return self.path / 'drawings'

    @property
    def model_path(self):
        return self.path / 'model'

    @property
    def model(self):
        if self._model is None:
            self.load_model()
        return self._model

    def load(self, path=None):
        if path:
            self.path = path

        assert self.path
        info = json.load(self.info_path.open())

        name = info.get('name')
        if not name:
            name = self.path.name
        self.name = name
        self.meaning = info.get('meaning')

        return self

    def load_drawings(self):
        self._drawings = []
        for drawing_path in self.drawings_path.glob('*'):
            drawing = TexnoMagicDrawing()
            drawing.load(drawing_path)
            self._drawings.append(drawing)

    def load_model(self):
        model = TexnoMagicSymbolModel(self.model_path)
        model.load()
        self._model = model

    def train_model(self, n_gauss=0):
        if not self._model:
            self._model = TexnoMagicSymbolModel(self.model_path)
        if n_gauss:
            self._model.n_gauss = n_gauss
        return self._model.train_symbol(self)

    def save(self):
        self.path.mkdir(parents=True, exist_ok=True)
        info = {
            'name': self.name,
            'meaning': self.meaning,
        }
        return json.dump(info, self.info_path.open('w'))

    def save_new_drawing(self, drawing):
        assert drawing

        if self._drawings is None:
            self.load_drawings()

        fn = "%s_%s.csv" % (common.name2fn(self.name), int(time.time() * 1000))
        drawing.path = self.drawings_path / fn
        drawing.save()
        return self._drawings.insert(0, drawing)

    @property
    def drawings(self):
        if self._drawings is None:
            self.load_drawings()
        return self._drawings

    def get_all_drawing_points(self):
        pp = [d.points for d in self.drawings]
        if pp:
            return np.concatenate(pp)
        return np.array([])

    def random_drawing(self):
        if self.drawings:
            return random.choice(self.drawings)
        return None

    def stats(self, full=False):
        if full:
            return '%s (%s): %s drawings @ %s' % (self.name, self.meaning, len(self.drawings), self.path)
        return '%s (%s)' % (self.name, self.meaning)

    def __repr__(self):
        return '<TexnoMagicSymbol %s>' % self.stats()
