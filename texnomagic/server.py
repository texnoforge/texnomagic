"""
TexnoMagic JSON-RPC over TCP server

This is a primary way to use TexnoMagic outside of Python.

You can start the server from terminal by invoking this module:

    python -m texnomagic.server

The server is using Godot Engine networking convention of 4 initial message
bytes marking the total message length and thus you can use Godot's native
networking or simply write a client of your own in a language of your choice.

Please see `client.py` for a reference implementation of a client.
"""
import logging
import socketserver
import sys

from texnomagic.jsonrpcserver import dispatch, ensure_jsonrpcserver

from texnomagic import __version__
from texnomagic import common
from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic.lang import TexnoMagicLanguage
# must be loaded in order for jsonrpc.dispatch() to work
from texnomagic import requests  # noqa


LOG_FORMAT = '[TexnoMagic] %(message).64s'
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=LOG_FORMAT)

DEFAULT_PORT = 6969


def serve(host='localhost', port=DEFAULT_PORT, abcs=None):
    """
    start TexnoMagic TCP server and serve forever
    """
    ensure_jsonrpcserver()

    logging.info("START TexnoMagic TCP server %s on %s:%s ..." % (__version__, host, port))
    if not abcs:
        abcs = TexnoMagicAlphabets()
        abcs.load()

    with socketserver.TCPServer((host, port), TexnoMagicTCPHandler) as server:
        server.context = {
            'abcs': abcs,
            'lang': TexnoMagicLanguage()
        }
        logging.info("alphabets: %s" % abcs.pretty())
        logging.info("server is RUNNING at %s:%s (CTRL+C to terminate)", host, port)
        try:
            server.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            logging.info("server is SHUTTING DOWN, bye o/")


class TexnoMagicTCPHandler(socketserver.BaseRequestHandler):
    """
    TexnoMagic JSON-RPC over TCP request handler

    Individual requests are processed in requests.py
    """
    def handle(self):
        logging.info("NEW STREAM: %s", self.client_address)
        while True:
            # self.request is the TCP socket connected to the client
            try:
                size_raw = self.request.recv(4)
            except ConnectionResetError:
                logging.info("CLOSED connection by client")
                return
            except ConnectionAbortedError:
                logging.info("ABORTED connection")
                return

            n_read = len(size_raw)
            if n_read == 0:
                logging.info("DISCONNECT (0 bytes read)")
                return
            elif n_read != 4:
                logging.warning("TOO FEW BYTES: %s", n_read)
                return
            size = common.bytes2int(size_raw)
            i = 0
            data_raw = bytes()
            while i < size:
                rest = size - i
                n = min(rest, common.BUFFER_SIZE)
                data_raw += self.request.recv(n)
                i += n
            data = data_raw.decode('utf-8')
            # please see requests.py for individual requests' code
            response = dispatch(data, context=self.server.context)
            if response:
                self.send_data(response)

    def finish(self):
        logging.info("STREAM CLOSED: %s", self.client_address)

    def send_data(self, data):
        raw_data = bytes(data.encode('utf-8'))
        head = common.int2bytes(len(raw_data))
        payload = head + raw_data
        return self.request.sendall(payload)


if __name__ == "__main__":
    # primitive TexnoMagic server module interface
    # $ python -m texnomagic.server 6969
    args = sys.argv[1:]
    port = DEFAULT_PORT
    if args:
        port = int(args[0])
    serve(port=port)
