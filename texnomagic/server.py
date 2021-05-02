"""
TexnoMagic TCP server
"""
import json
import logging
import socketserver
import sys

from texnomagic import __version__
from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic.lang import TexnoMagicLanguage
from texnomagic.drawing import TexnoMagicDrawing


LOG_FORMAT = '[TexnoMagic] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=LOG_FORMAT)


def serve(host='127.0.0.1', port=6969, abcs=None):
    logging.info("server %s starting..." % __version__)
    if not abcs:
        abcs = TexnoMagicAlphabets()
        abcs.load()

    with socketserver.TCPServer((host, port), TexnoMagicTCPHandler) as server:
        server.abcs = abcs
        server.lang = TexnoMagicLanguage()
        logging.info("alphabets: %s" % abcs.stats())
        logging.info("server is RUNNING at %s:%s (CTRL+C to terminate)", host, port)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("server is SHUTTING DOWN, bye o/")


class TexnoMagicTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        data_raw = self.request.recv(1024).strip()
        try:
            self.data = json.loads(data_raw)
        except Exception:
            return self.send_error("invalid data format - expecting JSON")
        if not self.data or 'query' not in self.data:
            return self.send_error('invalid request format')
        query = self.data.get('query')

        fun_name = 'query_%s' % query
        fun = getattr(self, fun_name, None)
        if fun is None:
            return self.send_error("unknown query: %s" % query)
        reply = fun()
        return self.send_data(reply)

    def query_spell(self):
        text = self.data.get('text')
        if not text:
            return self.send_error('missing required arg: text (spell to parse)', q='spell')
        try:
            spell = self.server.lang.parse(text)
            reply = {
                'query': 'spell',
                'status': 'ok',
                'reply': spell,
            }
        except Exception as e:
            reply = {
                'query': 'spell',
                'status': 'ok',
                'reply': {'spell': '', 'parse_error': str(e)},
            }
        return reply

    def query_symbol(self):
        abc_name = self.data.get('abc')
        if not abc_name:
            return self.send_error('missing required arg: abc (alphabet name)', q='symbol')
        curves = self.data.get('curves')
        if not curves:
            return self.send_error('missing required arg: curves (symbol points to recognize)', q='symbol')
        abc = self.server.abcs.get_abc_by_name(name=abc_name)
        if not abc:
            return self.send_error("requested alphabet isn't available: %s" % abc_name, q='symbol')

        drawing = TexnoMagicDrawing(curves=curves)
        symbol, score = abc.recognize(drawing)
        reply = {
            'query': 'symbol',
            'status': 'ok',
            'reply': {
                'symbol': symbol.meaning,
                'score': score,
            }
        }
        return reply

    def send_error(self, msg, q='error'):
        reply = {
            'query': q,
            'status': 'error',
            'error_message': msg,
        }
        return self.send_data(reply)

    def send_data(self, data):
        return self.request.sendall(bytes(json.dumps(data).encode('utf-8')))


if __name__ == "__main__":
    serve()
