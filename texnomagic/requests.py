"""
TexnoMagic RPC handling logic

Individual functions in this module marked with @jsonrpcserver.method decorator
are used for Remote Procedure Calls (RPC) by the TexnoMagic server.
"""
import logging

from jsonrpcserver import method
from jsonrpcserver.response import InvalidParamsResponse

from texnomagic import __version__
from texnomagic.drawing import TexnoMagicDrawing
from texnomagic import mods


@method
def spell(context, text):
    return context['lang'].parse(text)


@method
def symbol(context, abc, curves):
    _abc = context['abcs'].get_abc_by_name(name=abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)

    drawing = TexnoMagicDrawing(curves=curves)
    symbol, score = _abc.recognize(drawing)
    r = {
        'symbol': symbol.name,
        'score': score,
    }
    return r


@method
def train_symbol(context, abc, symbol):
    _abc = context['abcs'].get_abc_by_name(name=abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)
    _symbol = _abc.get_symbol_by_name(name=symbol)
    if not _symbol:
        raise ValueError("requested symbol isn't available: %s" % symbol)
    r = _symbol.train_model()
    assert(r)
    _symbol.model.save()
    return True


@method
def model_preview(context, abc, symbol):
    _abc = context['abcs'].get_abc_by_name(name=abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)
    _symbol = _abc.get_symbol_by_name(name=symbol)
    if not _symbol:
        raise ValueError("requested symbol isn't available: %s" % symbol)
    model = _symbol.model
    if not model:
        return {}
    p = model.get_preview()
    return p


@method
def download_mod(context, mod):
    all_mods = mods.get_online_mods()
    for m in all_mods:
        if m.name_id == mod or m.name == mod:
            m.download()
            return True
    return False


@method
def version(context):
    return __version__
