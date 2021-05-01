from pathlib import Path
import shutil
import tempfile

import pytest

from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic.abc import TexnoMagicAlphabet
from texnomagic.symbol import TexnoMagicSymbol
from texnomagic.model import TexnoMagicSymbolModel


# pytest parametrization doesn't play well with fixtures,
# need to solve this on module-level
BASE_PATH = Path(__file__).parents[1]
ABCS_PATH = BASE_PATH / 'alphabets'
assert ABCS_PATH.exists()
ABCS = TexnoMagicAlphabets({'test': ABCS_PATH})
ABCS.load()
ABC = ABCS.abcs['test'][0]
N_SYMBOLS = len(ABC.symbols)


@pytest.fixture(scope="module")
def abc(tmp_path_factory):
    """
    use a shared temporary copy of built-in testing alphabet in all tests
    """
    tmp_path = tmp_path_factory.mktemp('tenxomagic_tests')
    abc_path = tmp_path / ABC.base_path.name
    shutil.copytree(ABC.base_path, abc_path)

    abc = TexnoMagicAlphabet(base_path=abc_path)
    abc.load()
    return abc


@pytest.fixture(scope="module", params=range(N_SYMBOLS))
def symbol(abc, request):
    i = request.param
    return abc.symbols[i]


def test_symbol_model(symbol):
    symbol.train_model_from_drawings()
    drawing = symbol.get_random_drawing()
    score = symbol.model.score(drawing)
    assert score > -100
