"""
TexnoMagic TCP server
"""
import json
import logging
import socketserver
import sys

from texnomagic import __version__
from texnomagic import common
from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic.lang import TexnoMagicLanguage
from texnomagic.drawing import TexnoMagicDrawing


LOG_FORMAT = '[TexnoMagic] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=LOG_FORMAT)

DEFAULT_PORT = 6969


def serve(host='localhost', port=DEFAULT_PORT, abcs=None):
    logging.info("server %s starting on %s:%s ..." % (__version__, host, port))
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

            l = len(size_raw)
            if l == 0:
                logging.info("DISCONNECT (0 bytes read)")
                return
            elif l != 4:
                logging.info("TOO FEW BYTES: %s", l)
                return
            size = common.bytes2int(size_raw)
            i = 0
            data_raw = bytes()
            while i < size:
                rest = size - i
                n = min(rest, common.BUFFER_SIZE)
                data_raw += self.request.recv(n)
                i += n
            logging.info("REQUEST (%s): %s", size, data_raw[:80])
            try:
                self.data = json.loads(data_raw)
            except Exception:
                self.send_error("invalid data format - expecting JSON")
                continue
            try:
                query = self.data['query']
            except Exception:
                self.send_error('invalid request format - no query')
                continue
            query = self.data.get('query')

            fun_name = 'query_%s' % query
            fun = getattr(self, fun_name, None)
            if fun is None:
                self.send_error("unknown query: %s" % query)
                continue
            reply = fun()
            self.send_data(reply)

    def finish(self):
        logging.info("STREAM CLOSED: %s", self.client_address)

    def send_data(self, data):
        j = json.dumps(data)
        raw_data = bytes(j.encode('utf-8'))
        head = common.int2bytes(len(raw_data))
        payload = head + raw_data
        logging.info("RESPONSE (%s): %s", len(payload), j)
        return self.request.sendall(payload)

    def send_error(self, msg, q='error'):
        reply = {
            'query': q,
            'status': 'error',
            'error_message': msg,
        }
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

    def query_train_symbol(self):
        abc_name = self.data.get('abc')
        if not abc_name:
            return self.send_error('missing required arg: abc (alphabet name)', q='train_symbol')
        symbol_name = self.data.get('symbol')
        if not abc_name:
            return self.send_error('missing required arg: symbol (symbol name)', q='train_symbol')
        abc = self.server.abcs.get_abc_by_name(name=abc_name)
        if not abc:
            return self.send_error("requested alphabet isn't available: %s" % abc_name, q='train_symbol')
        symbol = abc.get_symbol_by_name(name=symbol_name)
        if not symbol:
            return self.send_error("requested symbol isn't available: %s" % symbol_name, q='train_symbol')
        logging.info("TRAIN SYMBOL model: %s" % symbol_name)
        r = symbol.train_model()
        assert(r)
        symbol.model.save()
        reply = {
            'query': 'train_symbol',
            'status': 'ok'
        }
        return reply

    def query_model_preview(self):
        q = 'model_preview'
        abc_name = self.data.get('abc')
        if not abc_name:
            return self.send_error('missing required arg: abc (alphabet name)', q=q)
        symbol_name = self.data.get('symbol')
        if not abc_name:
            return self.send_error('missing required arg: symbol (symbol name)', q=q)
        abc = self.server.abcs.get_abc_by_name(name=abc_name)
        if not abc:
            return self.send_error("requested alphabet isn't available: %s" % abc_name, q=q)
        symbol = abc.get_symbol_by_name(name=symbol_name)
        if not symbol:
            return self.send_error("requested symbol isn't available: %s" % symbol_name, q=q)
        model = symbol.model
        if not model:
            return self.send_error("no model for symbol: %s" % symbol_name, q=q)
        p = symbol.model.get_preview()
        reply = {
            'query': q,
            'preview': p,
            'status': 'ok'
        }
        return reply


if __name__ == "__main__":
    args = sys.argv[1:]
    port = DEFAULT_PORT
    if args:
        port = int(args[0])
    serve(port=port)
