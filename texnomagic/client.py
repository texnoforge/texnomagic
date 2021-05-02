"""
TexnoMagic TCP client
"""
import json
import socket


class TexnoMagicClient:
    def __init__(self, host='127.0.0.1', port=6969):
        self.host = host
        self.port = port
        self.sock = None
        self.buffer_size = 1024

    def connect(self):
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server and send data
        self.sock.connect((self.host, self.port))

    def request(self, query):
        data = json.dumps(query)
        self.sock.sendall(bytes(data + "\n", "utf-8"))
        reply = str(self.sock.recv(self.buffer_size), "utf-8")
        return json.loads(reply)

    def close(self):
        self.sock.close()
