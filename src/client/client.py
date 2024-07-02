import socket

from src.client.torrent_converter import TorrentConverter
from src.client.udp_socket import UDPSocket

from loguru import logger

from urllib.parse import urlparse
from io import BytesIO
import struct
import random


class BorrentClient:

    def __init__(self, path: str):
        self.path = path
        self.id = "-XD0001-" + "".join([str(random.randint(0, 9)) for i in range(12)])

    def exec(self):
        with open(self.path, "rb") as file:
            bin_torrent = file.read()

        torrent = TorrentConverter.into_torrent(bin_torrent)

        available_trackers = dict()
        for tracker_url in torrent.announce_list[0]:
            logger.info(f"Trying out {tracker_url}")

            parsed_tracker_url = urlparse(tracker_url)
            if not parsed_tracker_url.port:
                logger.info(f"Connection with {tracker_url} can't be established: port was not provided")
                continue

            sock = UDPSocket(dest_port=parsed_tracker_url.port, dest_host=parsed_tracker_url.hostname, timeout=2)
            request = struct.pack("!qii", 0x41727101980, 0, random.randint(-2 ** 31, 2 ** 31 - 1))

            try:
                sock.send(request)
            except socket.gaierror:
                logger.info(f"{tracker_url} is not available")
            else:
                try:
                    resp = sock.receive(1024)
                except TimeoutError:
                    logger.info(f"Connection to {tracker_url} timed out")
                else:
                    logger.info(f"Response from {tracker_url}: {resp}")
                    available_trackers[tracker_url] = resp
                    break

        for key in available_trackers.keys():
            resp = available_trackers[key]
            print(struct.unpack('!iiq', resp))






