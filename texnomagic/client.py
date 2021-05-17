"""
TexnoMagic TCP client
"""
import json
import socket

from texnomagic import common


class TexnoMagicClient:
    def __init__(self, host='localhost', port=6969):
        self.host = host
        self.port = port
        self.sock = None
        self.buffer_size = 1024

    def connect(self):
        # create a TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def request(self, query):
        data = json.dumps(query)
        body = bytes(data, "utf-8")
        head = common.int2bytes(len(body))
        payload = head + body
        self.sock.sendall(payload)
        head = self.sock.recv(4)
        size = common.bytes2int(head)
        reply = str(self.sock.recv(size), "utf-8")
        return json.loads(reply)

    def close(self):
        self.sock.close()
