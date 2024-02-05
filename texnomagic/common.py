import json
import yaml
import toml
import numpy as np
import os
from pathlib import Path
import re

from rich.syntax import Syntax

from texnomagic.console import console


DUMP_FORMATS = ['toml', 'yaml', 'json']
DUMP_FORMAT_DEFAULT = 'toml'

IMAGE_FORMATS = ['svg', 'png']
IMAGE_FORMAT_DEFAULT = 'svg'


def name2fn(name):
    fn = re.sub(r'\s+', '-', name.lower())
    return fn


def name2handle(name):
    return ''.join(ch for ch in name.lower() if ch.isalnum())


def get_data_path():
    appdata = os.environ.get('APPDATA')
    if appdata:
        # windows system
        p = Path(appdata)
    else:
        # normal system :)
        p = Path.home() / '.local/share'
    return p / 'WordsOfPower'


MIN_SCORE = 0.6

DATA_PATH = get_data_path()
USER_DATA_PATH = DATA_PATH / 'user'
MODS_DATA_PATH = DATA_PATH / 'mods'
EXPORT_PATH = DATA_PATH / 'export'

ALPHABETS_DIR = 'alphabets'
ALPHABETS_PATHS = {
    'user': USER_DATA_PATH / ALPHABETS_DIR,
    'mods': MODS_DATA_PATH / ALPHABETS_DIR,
}

BUFFER_SIZE = 1024

CORE_SYMBOLS_ORDER = [
    # elements
    'fire',
    'ice',
    'lightning',
    'water',
    'air',
    'earth',
    'life',
    'death',
    # shapes
    'bolt',
    'ball',
    'beam',
    'area',
    'cone',
    # targets
    'self',
    'friend',
    'enemy',
    # selectors
    'close',
    'far',
    'weak',
    'strong',
    'random',
    'all',
    # modifiers
    'big',
    'small',
    'fast',
    'slow',
    'homing',
]


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def int2bytes(x):
    return x.to_bytes(4, byteorder="little")


def bytes2int(b):
    return int.from_bytes(b, byteorder="little")


def pretty_dumps(data, format=DUMP_FORMAT_DEFAULT, indent=2):
    if format == 'toml':
        return toml.dumps(data)
    if format == 'yaml':
        return yaml.safe_dump(data, indent=indent, sort_keys=False)
    else:
        return json.dumps(data, indent=indent, sort_keys=False)


def pretty_print(data, format=DUMP_FORMAT_DEFAULT, **kwargs):
    str = pretty_dumps(data, format=format, **kwargs)
    syntax = Syntax(str, format)
    console.print(syntax)


def find_file_at_parents(fn, path=None):
    if path:
        path = Path(path)
    else:
        path = Path()
    cpath = path.absolute()

    while True:
        file_path = cpath / fn
        if file_path.exists():
            return file_path
        next_cpath = cpath.parent
        if next_cpath == cpath:
            break
        cpath = next_cpath

    return None
