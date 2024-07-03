from src.entities.torrent.torrent_converter import TorrentConverter
from src.network.udp_socket import UDPSocket
from src.entities.requests.connect import ConnectRequest
from src.entities.responses.connect import ConnectResponse
from src.network.tracker_connection import TrackerConnection

from src.exceptions.connection import InvalidTransactionException

from loguru import logger

from urllib.parse import urlparse
import random
import socket


class BorrentClient:

    def __init__(self, path: str):
        self.path = path
        self.id = "-XD0001-" + "".join([str(random.randint(0, 9)) for i in range(12)])

    def exec(self):
        with open(self.path, "rb") as file:
            bin_torrent = file.read()

        torrent = TorrentConverter.into_torrent(bin_torrent)

        # try:
        #     parsed_tracker_url, response = self._connect_to_tracker(announce_list=torrent.announce_list,
        #                                                             transaction_id=random.randint(-2 ** 31, 2 ** 31 - 1))
        # except TrackersNotAvailableException as exc:
        #     logger.info(exc.args[0])
        #     return
        #
        # sock = UDPSocket(parsed_tracker_url.hostname, parsed_tracker_url.port, 2)
        #
        # if response.transaction_id != transaction_id:
        #     logger.info("Transaction id's do not match")
        #     return
        #
        # bin_info = Encoder().encode(TorrentInfoConverter.into_dict(torrent.info))
        # hashed_info = sha1(bin_info).digest()
        #
        # length = 0
        # if isinstance(torrent.info, TorrentMultiFileInfo):
        #     for file in torrent.info.files:
        #         length += file.length
        # else:
        #     length = torrent.info.length
        #
        # announce = AnnounceRequest(
        #     connection_id=resp.connection_id,
        #     action=1,
        #     transaction_id=resp.transaction_id,
        #     info_hash=hashed_info,
        #     peer_id=self.id.encode(),
        #     downloaded=0,
        #     uploaded=0,
        #     left=length,
        #     event=0,
        #     ip_address=0,
        #     key=0,
        #     num_want=-1,
        #     port=0
        # ).to_binary()
        #
        # try:
        #     sock.send(announce)
        # except socket.gaierror:
        #     logger.info(f"{key} is not available")
        # else:
        #     try:
        #         resp = sock.receive(1024)
        #     except TimeoutError:
        #         logger.info(f"Connection to {key} timed out")
        #     else:
        #         logger.info(f"Response from {key}: {resp}")
        #         available_trackers[key] = resp
        #         break

    @staticmethod
    def _connect_to_tracker(announce_list: list, transaction_id: int) -> TrackerConnection:
        connect_request = ConnectRequest(transaction_id).to_binary()

        # searching for any available trackers of the torrent
        for tracker_url in announce_list[0]:
            logger.info(f"Trying out {tracker_url}")
            parsed_tracker_url = urlparse(tracker_url)

            if not parsed_tracker_url.port:
                logger.info(f"Connection with {tracker_url} can't be established: port was not provided")
                continue

            sock = UDPSocket(dest_port=parsed_tracker_url.port, dest_host=parsed_tracker_url.hostname, timeout=2)

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
                else:
                    logger.info(f"Response from {tracker_url}: {response_bin}")

                    response = ConnectResponse(response_bin)
                    if response.transaction_id != transaction_id:
                        raise InvalidTransactionException()

                    return TrackerConnection(url=parsed_tracker_url,
                                             sock=sock,
                                             connection_id=response.connection_id)

        raise TrackersNotAvailableException()

    @staticmethod
    def _announce_to_tracker()






