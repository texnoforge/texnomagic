"""
TexnoMagic / Words of Power mods interface

Use this to parse/download TexnoMagic alphabets as mods from https://wop.mod.io
"""
from io import BytesIO
import json
import requests
import zipfile

from texnomagic import common


MODIO_API_KEY = "2071808b470b7abc78fc289e5d3396d1"
MODIO_GAME_ID = 1986
MODIO_API_URL = "https://api.mod.io/v1"
MODIO_MODS_URL = "%s/games/%s/mods" % (MODIO_API_URL, MODIO_GAME_ID)


def get_online_mods():
    mods_data = get_online_mods_data()
    return data2mods(mods_data)


def get_online_mods_data():
    params = {
        'api_key': MODIO_API_KEY
    }
    r = requests.get(MODIO_MODS_URL, params=params)
    return json.loads(r.text)


def data2mods(data):
    mods = []
    for mod_data in data['data']:
        mod = WoPOnlineMod(mod_data)
        mods.append(mod)
    return mods


class WoPOnlineMod:
    data = {}
    name = None
    name_id = None
    filename = None
    profile_url = None
    binary_url = None
    logo_url = None

    def __init__(self, data=None):
        if data:
            self.load_from_data(data)

    def load_from_data(self, data):
        self.name = data.get('name')
        self.name_id = data.get('name_id')
        self.profile_url = data.get('profile_url')
        modfile = data.get('modfile', {})
        self.filename = modfile.get('filename')
        self.binary_url = modfile.get('download', {}).get('binary_url')
        self.logo_url = data.get('logo', {}).get('thumb_320x180')
        self.data = data

    def download(self, path=None):
        if not path:
            path = common.ALPHABETS_PATHS['mods']
        br = requests.get(self.binary_url)
        filebytes = BytesIO(br.content)
        zipf = zipfile.ZipFile(filebytes)
        zipf.extractall(path)

    def pretty_data(self):
        return json.dumps(self.data, indent=4, sort_keys=True)

    def __repr__(self):
        return '<WoPOnlineMod: %s @ %s>' % (self.name, self.profile_url)
