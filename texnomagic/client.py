"""
TexnoMagic JSON-RPC over TCP client reference implementation

This is only used for testing in TexnoMagic.

You can also look at wopeditor for a full-fledged TexnoMagic client
implementation in Godot Engine's GDScript:

https://github.com/texnoforge/wopeditor
"""
import json
import socket

from texnomagic import common


class TexnoMagicClient:
    """
    simple reference implementation of TexnoMagic TCP/JSONRPC client
    """
    def __init__(self, host='localhost', port=6969):
        self.host = host
        self.port = port
        self.sock = None
        self.buffer_size = 1024
        self.last_id = 0

    def connect(self):
        """
        connect to TexnoMagic TCP server
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def request(self, method, params=None):
        """
        send JSONRTC request over TCP and return response
        """
        self.last_id += 1
        # prepare JSONRTC payload
        if not params:
            params = []
        req = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': self.last_id
        }
        # SEND request to server
        body = bytes(json.dumps(req), "utf-8")
        # first 4 bytes is the length of the message
        head = common.int2bytes(len(body))
        payload = head + body
        self.sock.sendall(payload)

        # RECEIVE response from server
        head = self.sock.recv(4)
        # first 4 bytes is the length of the message
        size = common.bytes2int(head)
        reply = str(self.sock.recv(size), "utf-8")
        return json.loads(reply)

    def close(self):
        """
        close the connection to TexnoMagic TCP server
        """
        self.sock.close()
