"""
TexnoMagic RPC handling logic

Individual functions in this module marked with @jsonrpcserver.method decorator
are used for Remote Procedure Calls (RPC) by the TexnoMagic server.
"""
from jsonrpcserver import method

from texnomagic import __version__
from texnomagic.drawing import TexnoMagicDrawing
from texnomagic import mods


@method
def reload(context):
    context['abcs'].load()
    return True


@method
def spell(context, text):
    return context['lang'].parse(text)


@method
def recognize(context, abc, curves):
    if not curves:
        return []
    _abc = context['abcs'].get_abc_by_name(name=abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)

    drawing = TexnoMagicDrawing(curves=curves)
    drawing.normalize()
    symbol, score = _abc.recognize(drawing)
    r = {
        'symbol': symbol.name if symbol else None,
        'score': score,
    }
    return r


@method
def recognize_top(context, abc, curves, n=0):
    if not curves:
        return []
    _abc = context['abcs'].get_abc_by_name(name=abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)

    drawing = TexnoMagicDrawing(curves=curves)
    drawing.normalize()
    symbols = _abc.scores(drawing)
    symbols = [s for s in symbols if s[1] > 0]
    if n:
        n = int(n)
        symbols = symbols[:n]
    return [(s.name, score) for (s, score) in symbols]


@method
def train_symbol(context, abc, symbol, n_gauss=0):
    _abc = context['abcs'].get_abc_by_name(name=abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)
    _symbol = _abc.get_symbol_by_name(name=symbol)
    if not _symbol:
        raise ValueError("requested symbol isn't available: %s" % symbol)
    r = _symbol.train_model(n_gauss=n_gauss)
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
def export_abc(context, abc):
    _abc = context['abcs'].get_abc_by_name(name=abc)
    if not _abc:
        raise ValueError("requested alphabet isn't available: %s" % abc)
    return _abc.export()


@method
def version(context):
    return __version__
