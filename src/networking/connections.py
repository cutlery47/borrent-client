from src.networking.sockets import UDPSocket, TCPSocket

from src.exceptions.tracker import TrackerException

from src.entities.torrent.torrent_info import TorrentInfoConverter
from src.entities.torrent.torrent import Torrent, TorrentConverter
from src.entities.requests.announce import AnnounceRequest, AnnounceResponse

from bcoding import bencode

from loguru import logger

from urllib.parse import ParseResult
from hashlib import sha1

class TrackerConnection:

    def __init__(self, url: ParseResult, sock: UDPSocket, connection_id: int):
        self.url = url
        self.sock = sock
        self.connection_id = connection_id

    def announce(self, client_id: str, left: int, downloaded: int, uploaded: int, event: int, torrent: Torrent) -> AnnounceResponse:
        hashed = sha1(bencode(TorrentInfoConverter.into_dict(torrent.info))).digest()
        request = AnnounceRequest(
            connection_id=self.connection_id,
            action=1,
            transaction_id=1337,
            info_hash=hashed,
            peer_id=client_id.encode(),
            downloaded=downloaded,
            left=left,
            uploaded=uploaded,
            event=event,
            ip_address=0,
            key=1337,
            num_want=-1,
            port=self.sock.src_port if self.sock.src_port is not None else 0
        ).to_binary()

        logger.info(f"Sending announce request to {self.url.geturl()}")
        self.sock.send(request, dest_host=self.url.hostname, dest_port=self.url.port)
        try:
            bin_response = self.sock.receive(1024)
        except TimeoutError:
            self.sock.close()
            logger.info(f"Announce connection to {self.url.geturl()} timed out")
            raise TrackerException('Could not send announce request to the tracker')
        else:
            logger.info(f"Announce response from {self.url.geturl()}: {bin_response}")
            response = AnnounceResponse(bin_response)
            return response

    def scrape(self):
        pass

class PeerConnection:

    def __init__(self, sock: TCPSocket):
        self.sock = sock