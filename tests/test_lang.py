from pathlib import Path
import os
import re

import pytest

from texnomagic.lang import TexnoMagicLanguage


BASE_PATH = Path(__file__).parents[2]


@pytest.fixture(scope="module")
def txm():
    """
    test global instance of TexnoMagicLanguage
    """
    return TexnoMagicLanguage()


def test_bolt(txm):
    spell = txm.parse("big big ice fire death fast homing bolt random")
    exp = {
        "spell": "bolt",
        "effect": [
            "ice",
            "fire",
            "death"
        ],
        "effect_mods": {
            "size": 4
        },
        "spell_mods": {
            "speed": 2,
            "homing": 1
        },
        "direction": "random"
    }
    assert spell == exp


def test_self(txm):
    spell = txm.parse("big small big earth life self")
    exp = {
        "spell": "self",
        "effect": [
            "earth",
            "life"
        ],
        "effect_mods": {
            "size": 2.0
        }
    }
    assert spell == exp


def test_shield(txm):
    spell = txm.parse("small fast death ice shield area")
    exp = {
        "spell": "shield",
        "shape": "area",
        "effect": [
            "death",
            "ice"
        ],
        "effect_mods": {
            "size": 0.5,
            "speed": 2
        }
    }
    assert spell == exp
