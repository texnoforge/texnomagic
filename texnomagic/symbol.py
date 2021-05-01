import json
import numpy as np
import os
import random
import time

from texnomagic import common
from texnomagic.drawing import TexnoMagicDrawing
from texnomagic.model import TexnoMagicSymbolModel


class TexnoMagicSymbol:
    def __init__(self, name=None, meaning=None, base_path=None):
        self.name = name
        self.meaning = meaning
        self.base_path = base_path
        self._drawings = None
        self._model = None

    @property
    def info_path(self):
        return self.base_path / 'texno_symbol.json'

    @property
    def drawings_path(self):
        return self.base_path / 'drawings'

    @property
    def model_path(self):
        return self.base_path / 'model'

    @property
    def model(self):
        if self._model is None:
            self.load_model()
        return self._model

    def load(self, base_path=None):
        if base_path:
            self.base_path = base_path

        assert self.base_path
        info = json.load(self.info_path.open())

        name = info.get('name')
        if not name:
            name = self.base_path.name
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
        model = TexnoMagicSymbolModel()
        model.load(self.model_path)
        self._model = model

    def save(self):
        os.makedirs(self.base_path, exist_ok=True)
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
        return np.concatenate([d.points for d in self.drawings])

    def get_random_drawing(self):
        if self.drawings:
            return random.choice(self.drawings)
        return None

    def train_model_from_drawings(self):
        return self.model.train_symbol(self)

    def __repr__(self):
        return '<TexnoMagicSymbol %s (%s) @ %s>' % (self.name, self.meaning, self.base_path)
