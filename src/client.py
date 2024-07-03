from src.entities.torrent.torrent_converter import TorrentConverter
from src.entities.torrent.torrent import Torrent
from src.entities.requests.connect import ConnectRequest, ConnectResponse

from src.networking.udp_socket import UDPSocket
from src.networking.tracker_connection import TrackerConnection

from src.exceptions.connection import UnavailableTrackersException

from loguru import logger

from borrent_parser.decoder import Decoder

from urllib.parse import urlparse
import random
import socket
import traceback


class BorrentClient:

    def __init__(self, path: str, port: int = 6889):
        self.path = path
        self.port = port
        self.id = "-XD0001-" + "".join([str(random.randint(0, 9)) for _ in range(12)])

    def exec(self):
        with open(self.path, "rb") as file:
            bin_torrent = file.read()

        torrent_dict = Decoder().decode(bin_torrent)
        torrent = TorrentConverter.into_torrent(bin_torrent)

        try:
            tracker_connection = self._connect_to_tracker(torrent=torrent)
        except UnavailableTrackersException as exc:
            logger.info(exc.args[0])
            return

        try:
            tracker_connection.announce(self.id)
        except Exception as exc:
            logger.error(exc.args[0])
            logger.error(traceback.format_exc())
            return

        tracker_connection.sock.close()

    def _connect_to_tracker(self, torrent: Torrent) -> TrackerConnection:
        # searching for any available trackers of the torrent
        for tracker_url in torrent.announce_list:
            transaction_id = random.randint(-2 ** 31, 2 ** 31 - 1)
            connect_request = ConnectRequest(transaction_id).to_binary()

            logger.info(f"Trying out {tracker_url}")
            parsed_tracker_url = urlparse(tracker_url[0])

            if not parsed_tracker_url.port:
                logger.info(f"Connection with {tracker_url} can't be established: port was not provided")
                continue

            sock = UDPSocket(dest_port=parsed_tracker_url.port,
                             dest_host=parsed_tracker_url.hostname,
                             src_port=self.port,
                             timeout=1)

            # sending connect request
            try:
                sock.send(connect_request)
            except socket.gaierror:
                # hostname is invalid
                logger.info(f"{tracker_url} is invalid")
                sock.close()
            else:
                # receiving connect response
                try:
                    response_bin = sock.receive(1024)
                except TimeoutError:
                    logger.info(f"Connection to {tracker_url} timed out")
                    sock.close()
                else:
                    logger.info(f"Response from {tracker_url}: {response_bin}")

                    response = ConnectResponse(response_bin)

                    if response.transaction_id != transaction_id:
                        logger.info(f"Invalid transaction id sent by {tracker_url}")
                        sock.close()
                    else:
                        return TrackerConnection(url=parsed_tracker_url,
                                                 sock=sock,
                                                 connection_id=response.connection_id,
                                                 torrent=torrent)
        raise UnavailableTrackersException()
