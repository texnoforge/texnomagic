import json
import numpy as np
import random
import time
from pathlib import Path

from texnomagic import common
from texnomagic.drawing import TexnoMagicDrawing
from texnomagic.model import TexnoMagicSymbolModel


INFO_FILE = 'texno_symbol.json'


class TexnoMagicSymbol:
    """TexnoMagic Symbol has:

    * `name`: arbitrary unicode string without spaces
    * `meaning`: english meaning in lowercase
    * `path`: path to Symbol dir

    Symbol can optionally contain:

    * `drawings`: a set of [Drawings][texnomagic.drawing.TexnoMagicDrawing]
    * `images`: images of the symbol in different formats (primary SVG)
    * `model`: model for symbol recognition

    Symbols usually reside within an [Alphabet][texnomagic.abc.TexnoMagicAlphabet].

    This class provides convenient utilities for working with TexnoMagic Symbols,
    see individual methods.
    """
    def __init__(self, path=None, meaning=None, name=None):
        if path and path.name.lower() == INFO_FILE:
            # accept path to symbol info file as well
            path = path.parent

        self.path = path
        self.name = name
        self.meaning = meaning
        self._drawings = None
        self._images = None
        self._model = None

    @property
    def info_path(self) -> Path:
        f"""Path to Symbol `{INFO_FILE}` info file."""
        return self.path / INFO_FILE

    @property
    def drawings_path(self) -> Path:
        """Path to Symbol `drawings` dir."""
        return self.path / 'drawings'

    @property
    def model_path(self) -> Path:
        """Path to Symbol `model` dir."""
        return self.path / 'model'

    @property
    def image_base_path(self) -> Path:
        """Path to Symbol `image` dir."""
        return self.path / 'image'

    @property
    def handle(self) -> str:
        """Symbol handle (lowercase string)."""
        return common.name2handle(self.name)

    @property
    def model(self) -> TexnoMagicSymbolModel:
        """Symbol model.

        Use `symbol.model.ready` to check if there is actually an usable model."""
        if self._model is None:
            self.load_model()
        return self._model

    def get_image_path(self, format=common.IMAGE_FORMAT_DEFAULT) -> Path:
        return self.image_base_path / f'symbol.{format}'

    def get_images(self) -> dict:
        imgs = {}
        for format in common.IMAGE_FORMATS:
            image_path = self.get_image_path(format=format)
            if image_path.exists():
                imgs[format] = image_path
        return imgs

    @property
    def images(self) -> dict:
        """A dict of available Symbol images with format as key."""
        if self._images is None:
            self._images = self.get_images()
        return self._images

    def load(self, path=None):
        f"""Load Symbol metadata from info file ({INFO_FILE})."""
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
        """Load Symbol drawings from `drawings` dir."""
        self._drawings = []
        for drawing_path in self.drawings_path.glob('*'):
            drawing = TexnoMagicDrawing()
            drawing.load(drawing_path)
            self._drawings.append(drawing)

    def load_model(self):
        """Load Symbol model."""
        self._model = TexnoMagicSymbolModel(self.model_path)
        self._model.load()

    def train_model(self, n_gauss=0):
        """Train Symbol model from drawings."""
        if not self._model:
            self._model = TexnoMagicSymbolModel(self.model_path)
        if n_gauss:
            self._model.n_gauss = n_gauss
        return self._model.train_symbol(self)

    def save(self):
        """Save the Symbol into path."""
        self.path.mkdir(parents=True, exist_ok=True)
        info = {
            'name': self.name,
            'meaning': self.meaning,
        }
        return json.dump(info, self.info_path.open('w'))

    def save_new_drawing(self, drawing):
        """Save new Drawing into `drawings` dir."""
        assert drawing

        if self._drawings is None:
            self.load_drawings()

        fn = "%s_%s.csv" % (common.name2fn(self.name), int(time.time() * 1000))
        drawing.path = self.drawings_path / fn
        drawing.save()
        return self._drawings.insert(0, drawing)

    @property
    def drawings(self) -> list[TexnoMagicDrawing]:
        """A list of Symbol drawings in `drawings` dir.

        Lazy loaded on-demand.
        """
        if self._drawings is None:
            self.load_drawings()
        return self._drawings

    def get_all_drawing_points(self) -> np.array:
        """Get a list of all points from all drawings."""
        pp = [d.points for d in self.drawings]
        if pp:
            return np.concatenate(pp)
        return np.array([])

    def random_drawing(self) -> TexnoMagicDrawing:
        """Get a random drawing."""
        if self.drawings:
            return random.choice(self.drawings)
        return None

    def normalize(self):
        """Normalize all drawings. Overwrites files.

        See [texnomagic.drawing.TexnoMagicDrawing.normalize]."""
        for d in self.drawings:
            if d.points.any():
                d.normalize()
                d.save()

    def as_dict(self) -> dict:
        """Return Symbol as a dict."""
        images = {f: str(p.relative_to(self.path)) for f, p in self.images.items()}
        d = {
            'name': self.name,
            'meaning': self.meaning,
            'path': str(self.path),
            'n_drawings': len(self.drawings),
            'images': images,
        }
        if self.model:
            d['model'] = self.model.as_dict(relative_to=self.path)
        return d

    def pretty(self, drawings=False, images=False, model=False, path=False) -> str:
        """Pretty Symbol string with colors in rich formatting."""
        s = f'[bright_green]{self.name}[/]'
        if self.name != self.meaning:
            s += f' ([green]{self.meaning}[/])'

        extras = []
        if images and self.images:
            fmts = [f'[blue]{f.upper()}[/]' for f in self.images.keys()]
            extras.append(f"{', '.join(fmts)} image")
        if drawings and self.drawings:
            extras.append(f'[white]{len(self.drawings)}[/] drawings')
        if model and self.model.ready:
            extras.append(f'{self.model.pretty()}')
        if extras:
            s += f": {', '.join(extras)}"

        if path:
            s += f' @ [white]{self.path}[/]'

        return s

    def __str__(self) -> str:
        return f'{self.name} ({self.meaning})'

    def __repr__(self) -> str:
        return '<TexnoMagicSymbol %s>' % self.__str__()


def find_symbol_at_path(path=None) -> TexnoMagicSymbol | None:
    f"""Find Symbol at path (and parents) by {INFO_FILE} info file."""
    info = common.find_file_at_parents(INFO_FILE, path)
    if info:
        return TexnoMagicSymbol(info)
    return None
