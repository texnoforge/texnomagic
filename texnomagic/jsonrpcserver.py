from texnomagic.console import console
JSONRPCSERVER_AVAILABLE = False


def jsonrpcserver_not_available():
    console.print("[red]Python module required for this operation isn't available: [bold]jsonrpcserver[/][/]")
    raise ex.ModuleNotAvailable('jsonrpcserver')


def ensure_jsonrpcserver():
    if not JSONRPCSERVER_AVAILABLE:
        jsonrpcserver_not_available()


try:
    from jsonrpcserver import dispatch, method, Success
    JSONRPCSERVER_AVAILABLE = True
except ImportError:
    from texnomagic import ex

    # dummy classes for when jsonrpcserver is unavailable
    def method(func):
        return func

    dispatch = jsonrpcserver_not_available

    class Success:
        def __init__(self, *_args, **_kwargs):
            jsonrpcserver_not_available()
