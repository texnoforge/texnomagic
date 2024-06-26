"""
TexnoMagic RPC handling logic

Individual functions in this module marked with @jsonrpcserver.method decorator
are used for Remote Procedure Calls (RPC) by the TexnoMagic server.
"""
from texnomagic.jsonrpcserver import method, Success

from texnomagic import __version__
from texnomagic.drawing import TexnoMagicDrawing
from texnomagic import mods


@method
def reload(context):
    context['abcs'].load()
    return Success(True)


@method
def spell(context, text):
    return Success(context['lang'].parse(text))


@method
def recognize(context, abc, curves):
    if not curves:
        return []
    _abc = context['abcs'].get_alphabet(abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)

    drawing = TexnoMagicDrawing(curves=curves)
    drawing.normalize()
    symbol, score = _abc.recognize(drawing)
    r = {
        'symbol': symbol.name if symbol else None,
        'score': score,
    }
    return Success(r)


@method
def recognize_top(context, abc, curves, n=0):
    if not curves:
        return []
    _abc = context['abcs'].get_alphabet(name=abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)

    drawing = TexnoMagicDrawing(curves=curves)
    drawing.normalize()
    symbols = _abc.scores(drawing)
    symbols = [s for s in symbols if s[1] > 0]
    if n:
        n = int(n)
        symbols = symbols[:n]
    return Success([(s.name, score) for (s, score) in symbols])


@method
def train_symbol(context, abc, symbol, n_gauss=0):
    _abc = context['abcs'].get_alphabet(abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)
    _symbol = _abc.get_symbol(symbol)
    if not _symbol:
        raise ValueError("requested symbol isn't available: %s" % symbol)
    r = _symbol.train_model(n_gauss=n_gauss)
    assert(r)
    _symbol.model.save()
    return Success(True)


@method
def model_preview(context, abc, symbol):
    _abc = context['abcs'].get_alphabet(abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)
    _symbol = _abc.get_symbol(symbol)
    if not _symbol:
        raise ValueError("requested symbol isn't available: %s" % symbol)
    model = _symbol.model
    if not model:
        return {}
    p = model.get_preview()
    return Success(p)


@method
def download_mod(context, mod):
    all_mods = mods.get_online_mods()
    for m in all_mods:
        if m.name_id == mod or m.name == mod:
            m.download()
            return Success(True)
    return Success(False)


@method
def export_abc(context, abc):
    _abc = context['abcs'].get_alphabet(abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)
    return Success(_abc.export())


@method
def version(context):
    return Success(__version__)
