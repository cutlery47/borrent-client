from src.exceptions.socket import ConnectionException

from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM, socket


class TCPSocket:

    def __init__(self, dest_host, dest_port, timeout, src_port: int = None):
        self.src_port = src_port
        self.dest_host = dest_host
        self.dest_port = dest_port

        self._socket = socket(family=AF_INET, type=SOCK_STREAM)
        self._socket.settimeout(timeout)

        if self.src_port is not None:
            self._socket.bind(('0.0.0.0', self.src_port))

    def connect(self) -> bool:
        try:
            self._socket.connect((self.dest_host, self.dest_port))
        except (TimeoutError, ConnectionRefusedError):
            raise ConnectionException()
        return True

    def send(self, data: bytes):
        self._socket.send(data)

    def receive(self, bufsize) -> bytes:
        data = self._socket.recv(bufsize)
        return data

    def close(self):
        self._socket.close()


class UDPSocket:

    def __init__(self, timeout: int, src_port: int = None, blocking: bool = True):
        self.src_port = src_port

        self._socket = socket(family=AF_INET, type=SOCK_DGRAM, )
        self._socket.settimeout(timeout)
        if not blocking:
            self._socket.setblocking(False)

        if self.src_port is not None:
            self._socket.bind(('0.0.0.0', self.src_port))

    def send(self, data: bytes, dest_host: str, dest_port: int):
        self._socket.sendto(data, (dest_host, dest_port))

    def receive(self, bufsize: int) -> bytes:
        data = self._socket.recv(bufsize)
        return data

    def close(self):
        self._socket.close()