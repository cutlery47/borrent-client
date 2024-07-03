from src.networking.udp_socket import UDPSocket

from src.entities.torrent.torrent_converter import TorrentInfoConverter, TorrentConverter
from src.entities.torrent.torrent import Torrent
from src.entities.requests.announce import AnnounceRequest, AnnounceResponse

from borrent_parser.encoder import Encoder

from loguru import logger

from urllib.parse import ParseResult
from hashlib import sha1
import random

class TrackerConnection:

    def __init__(self, url: ParseResult, sock: UDPSocket, connection_id: int, torrent: Torrent):
        self.url = url
        self.sock = sock
        self.connection_id = connection_id
        self.torrent = torrent

    def peers(self):
        pass

    def announce(self, client_id: str):
        size = self.torrent.info.size()

        bin_info = Encoder().encode(TorrentInfoConverter.into_dict(self.torrent.info))
        hasher = sha1()
        hasher.update(bin_info)

        request = AnnounceRequest(
            connection_id=self.connection_id,
            action=1,
            transaction_id=random.randint(-2 ** 31, 2 ** 31 - 1),
            info_hash=hasher.digest(),
            peer_id=client_id.encode(),
            downloaded=0,
            left=size,
            uploaded=0,
            event=0,
            ip_address=0,
            key=random.randint(-2 ** 31, 2 ** 31 - 1),
            num_want=-1,
            port=self.sock.src_port
        ).to_binary()

        logger.info(f"Sending announce request to {self.url.geturl()}")
        self.sock.send(request)
        try:
            bin_response = self.sock.receive(1024)
        except TimeoutError:
            logger.info(f"Announce connection to {self.url.geturl()} timed out")
            self.sock.close()
            return
        else:
            logger.info(f"Announce response from {self.url.geturl()}: {bin_response}")
            response = AnnounceResponse(bin_response)
            print(response)

    def scrape(self):
        pass

