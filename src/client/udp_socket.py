from socket import socket, AF_INET, SOCK_DGRAM


class UDPSocket:

    def __init__(self, dest_host: str, dest_port: int, timeout: int):
        self.dest_host = dest_host
        self.dest_port = dest_port
        self._socket = socket(family=AF_INET, type=SOCK_DGRAM)
        self._socket.settimeout(timeout)

    def send(self, data: bytes):
        self._socket.sendto(data, (self.dest_host, self.dest_port))

    def receive(self, bufsize: int) -> bytes:
        data = self._socket.recv(bufsize)
        return data

