import json
import numpy as np
import random
import shutil
import time

from texnomagic import common
from texnomagic import ex
from texnomagic.drawing import TexnoMagicDrawing
from texnomagic.model import TexnoMagicSymbolModel


INFO_FILE = 'texno_symbol.json'


class TexnoMagicSymbol:
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
    def info_path(self):
        return self.path / INFO_FILE

    @property
    def drawings_path(self):
        return self.path / 'drawings'

    @property
    def model_path(self):
        return self.path / 'model'

    @property
    def image_base_path(self):
        return self.path / 'image'

    @property
    def handle(self):
        return common.name2handle(self.name)

    @property
    def model(self):
        if self._model is None:
            self.load_model()
        return self._model

    def get_image_path(self, format=common.IMAGE_FORMAT_DEFAULT):
        return self.image_base_path / f'symbol.{format}'

    def get_images(self):
        imgs = {}
        for format in common.IMAGE_FORMATS:
            image_path = self.get_image_path(format=format)
            if image_path.exists():
                imgs[format] = image_path
        return imgs

    @property
    def images(self):
        if self._images is None:
            self._images = self.get_images()
        return self._images

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
        self._model = TexnoMagicSymbolModel(self.model_path)
        self._model.load()

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

    def export_image(
            self,
            out_path,
            format=common.IMAGE_FORMAT_DEFAULT,
            **kwargs):

        image_path = self.get_image_path(format=format)
        if image_path.exists():
            # just copy over existing image
            shutil.copy(image_path, out_path)
            return True

        if format == 'png':
            image_path = self.get_image_path(format='svg')
            if image_path.exists():
                # TODO: export symbol.svg to PNG
                print("TODO: convert symbol.svg to PNG")

        d = self.random_drawing()
        if d:
            # no image present - render from random curve
            d.export(out_path, format=format, **kwargs)
            return True

        raise ex.ImageNotFound()

    def as_dict(self):
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

    def __str__(self):
        return f'{self.name} ({self.meaning})'

    def __repr__(self):
        return '<TexnoMagicSymbol %s>' % self.__str__()


def find_symbol_at_path(path=None):
    info = common.find_file_at_parents(INFO_FILE, path)
    if info:
        return TexnoMagicSymbol(info)
    return None
