import json
import numpy as np
import os
from pathlib import Path
import re


def name2fn(name):
    fn = re.sub(r'\s+', '-', name.lower())
    return fn


def get_data_path():
    appdata = os.environ.get('APPDATA')
    if appdata:
        # windows system
        p = Path(appdata) / 'Words of Power'
    else:
        # normal system :)
        p = Path.home() / '.words_of_power'
    return p


DATA_PATH = get_data_path()
USER_DATA_PATH = DATA_PATH / 'user'
MODS_DATA_PATH = DATA_PATH / 'mods'
EXPORT_PATH = DATA_PATH / 'export'

ALPHABETS_DIR = 'alphabets'
ALPHABETS_PATHS = {
    'user': USER_DATA_PATH / ALPHABETS_DIR,
    'mods': MODS_DATA_PATH / ALPHABETS_DIR,
}

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
