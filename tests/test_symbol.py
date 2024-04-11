import shutil

import pytest

from texnomagic.abc import TexnoMagicAlphabet
from texnomagic.model import TexnoMagicSymbolModel
from texnomagic import common

import commontest  # common testing code


@pytest.fixture(scope="module")
def abc(tmp_path_factory):
    """
    use a shared temporary copy of built-in testing alphabet in all tests
    """
    tmp_path = tmp_path_factory.mktemp('tenxomagic_tests')
    abc_path = tmp_path / commontest.ABC.path.name
    shutil.copytree(commontest.ABC.path, abc_path)

    abc = TexnoMagicAlphabet(path=abc_path)
    abc.load()
    abc.train_models()
    return abc


@pytest.fixture(scope="module", params=range(commontest.N_SYMBOLS))
def symbol(abc, request):
    i = request.param
    return abc.symbols[i]


def test_symbol_model_io(symbol):
    assert symbol.model.gmm
    drawing = symbol.random_drawing()
    score_orig = symbol.model.score(drawing)
    assert score_orig > -100

    model = TexnoMagicSymbolModel(path=symbol.model.path)
    model.load()
    score_new = model.score(drawing)

    # this means model save/load probably works :)
    assert score_new == score_orig


def test_symbol_model_recognize(abc):
    n_fail = 0
    for s in abc.symbols:
        d = s.random_drawing()
        sr, score = abc.recognize(d)
        if score >= common.MIN_SCORE:
            # correct symbol recognized
            assert sr == s
        else:
            # bellow minimal score
            assert sr is None
            print(f"recognition fail: {s} (score: {score})")
            n_fail += 1

    assert n_fail < 10, f"too many recognition fails: {n_fail}"
