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


def test_req_invalid_method(client):
    reply = client.request('KEKW')
    assert 'error' in reply
    error = reply['error']
    assert error == {
        'code': -32601,
        'message': 'Method not found',
        'data': 'KEKW',
    }


def test_req_spell(client):
    reply = client.request(
        'spell',
        ['big slow ice death fast homing bolt random'],
    )
    assert 'error' not in reply
    assert 'result' in reply
    result = reply['result']
    assert result == {
        'direction': 'random',
        'effect': ['ice', 'death'],
        'effect_mods': {'size': 2, 'speed': 0.5},
        'spell': 'bolt',
        'spell_mods': {'homing': 1, 'speed': 2},
    }


def test_req_recognize(client):
    reply = client.request(
        'recognize',
        {
            'abc': commontest.ABC.name,
            'curves': [[[1,1], [10,10], [100, 100]]],
        })
    assert isinstance(reply, dict)
    assert 'error' not in reply
    assert 'result' in reply
    result = reply['result']
    assert 'symbol' in result
    assert 'score' in result
