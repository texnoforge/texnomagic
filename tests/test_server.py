import multiprocessing
from pathlib import Path
from time import sleep

import pytest

from texnomagic.client import TexnoMagicClient
from texnomagic.server import serve

import commontest  # common testing code


@pytest.fixture(autouse=True, scope="session")
def start_server():
    p = multiprocessing.Process(
        target=serve,
        kwargs={'abcs': commontest.ABCS})
    p.start()
    # give the server some time to start
    sleep(0.2)
    yield
    p.terminate()


@pytest.fixture(scope="function")
def client():
    c = TexnoMagicClient()
    c.connect()
    yield c
    c.close()


def test_invalid_query(client):
    reply = client.request({'test': 'kek'})
    assert reply == {
        "query": "error",
        "status": "error",
        "error_message": "invalid request format - no query",
    }


def test_spell_query_valid(client):
    reply = client.request({
        'query': 'spell',
        'text': 'big slow ice death fast homing bolt random',
    })
    exp = {
        "query": "spell",
        "status": "ok",
        "reply": {
            "spell": "bolt",
            "effect": ["ice", "death"],
            "effect_mods": {"size": 2, "speed": 0.5},
            "spell_mods": {"speed": 2, "homing": 1},
            "direction": "random",
        }
    }
    assert reply == exp

def test_spell_query_invalid(client):
    reply = client.request({
        'query': 'spell',
        'text': 'big fire fail',
    })
    exp = {
        "query": "spell",
        "status": "ok",
        "reply": {
            "spell": "",
            "parse_error": "Rule 'mod_size' didn't match at 'fail' (line 1, column 10).",
        }
    }
    assert reply == exp


def test_symbol_query(client):
    reply = client.request({
        'query': 'symbol',
        'abc': commontest.ABC.name,
        'curves': [[[1,1], [10,10], [100, 100]]]
    })
    assert reply['query'] == 'symbol'
    assert reply['status'] == 'ok'
    assert reply['reply']['symbol']
    assert reply['reply']['score'] < 0
