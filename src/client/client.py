from src.client.torrent_converter import TorrentConverter
from src.client.udp_socket import UDPSocket
from src.entities.tracker.request import TrackerRequest
from src.entities.tracker.response import TrackerResponse

from urllib.parse import urlparse
import random

# TODO: fix announce list
# TODO: create tracker request

class BorrentClient:

    def __init__(self, path: str, host: str, port: int):
        self.path = path
        self.host = host
        self.port = port
        self.id = "-XD0001-" + "".join([str(random.randint(0, 9)) for i in range(12)])

    def exec(self):
        with open(self.path, "rb") as file:
            bin_meta = file.read()

        torrent = TorrentConverter.into_torrent(bin_meta)
        url = urlparse(torrent.announce)

        print(torrent)

        socket = UDPSocket(dest_host=url.hostname, dest_port=url.port, src_host=self.host, src_port=self.port)

        socket.send(b"123123")






