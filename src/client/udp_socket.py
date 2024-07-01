from socket import socket, AF_INET, SOCK_DGRAM


class UDPSocket:

    def __init__(self, dest_host: str, dest_port: int, src_host: str, src_port: int):
        self.dest_host = dest_host
        self.dest_port = dest_port
        self.src_host = src_host
        self.src_port = src_port

        self._socket = socket(family=AF_INET, type=SOCK_DGRAM)
        self._socket.bind((src_host, src_port))

    def send(self, data: bytes):
        self._socket.sendto(data, (self.dest_host, self.dest_port))

    def receive(self, bufsize: int) -> bytes:
        data = self._socket.recv(bufsize)
        return data

