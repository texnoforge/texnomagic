import multiprocessing
from pathlib import Path

import pytest

from texnomagic.abcs import TexnoMagicAlphabets
import commontest  # common testing code


def test_abcs_basic():
    abcs = commontest.ABCS
    assert len(abcs.abcs) == 1, "only one abc should be loaded"

    abc = abcs.get_abc_by_name("DEFINITELY NOT EXISTING")
    assert abc is None

    abc = abcs.get_abc_by_name(commontest.ABC.name)
    assert abc.name == commontest.ABC.name
