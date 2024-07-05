from src.entities.torrent.torrent import Torrent, TorrentConverter

from src.entities.requests.connect import ConnectRequest, ConnectResponse
from src.entities.requests.announce import AnnounceResponse

from src.networking.sockets import UDPSocket, TCPSocket
from src.networking.connections import TrackerConnection, PeerConnection

from src.exceptions.tracker import (UnavailableTrackersException, TrackerException, InvalidTransactionException,
                                    InvalidURLException)
from src.exceptions.socket import ConnectionException, SocketException

from loguru import logger
from typing import List
from urllib.parse import urlparse, ParseResult
import random
import socket
import traceback

class BorrentClient:

    def __init__(self, path: str, port: int = 6889):
        with open(path, "rb") as file:
            self.torrent = TorrentConverter.into_torrent(file.read())

        self.port = port
        self.id = "-XD0001-" + "".join([str(random.randint(0, 9)) for _ in range(12)])

    def start(self):

        # collecting all available trackers
        try:
            tracker_connections = self._connect_to_trackers(self.torrent)
        except Exception as exc:
            logger.info(exc.args[0])
            logger.error(traceback.format_exc())
            return

        # announcing ourselves to each tracker
        try:
            tracker_announce_responses = self._send_announces(tracker_connections)
        except Exception as exc:
            logger.info(exc.args[0])
            logger.error(traceback.format_exc())
            return

        tracker_peers = self._get_tracker_peers(tracker_announce_responses)
        tracker = self._get_best_tracker(tracker_peers)
        print(tracker)

    def _connect_to_trackers(self, torrent: Torrent) -> [TrackerConnection]:
        # list of all established connections
        tracker_connections = []
        # searching for any available trackers of the torrent
        for tracker_url in torrent.announce_list:
            # creating a distinct udp socket for each tracker connection
            sock = UDPSocket(timeout=1)
            # creating connect request
            transaction_id = 1337
            connect_request = ConnectRequest(transaction_id).to_binary()

            logger.info(f"Trying out {tracker_url}")
            parsed_tracker_url = urlparse(tracker_url[0])
            # check, if url can be parsed in the first place :)
            if not parsed_tracker_url.port:
                logger.info(f"Connection with {tracker_url} can't be established: port was not provided")
                continue

            # sending connect request
            try:
                self._send_connect(sock=sock,
                                   request=connect_request,
                                   parsed_tracker_url=parsed_tracker_url)
            except InvalidURLException as exc:
                logger.info(exc.args[0])
                continue

            # receiving connect response
            try:
                response = self._receive_connect(sock=sock,
                                                 transaction_id=transaction_id,
                                                 parsed_tracker_url=parsed_tracker_url)
                # converting it to connection
                tracker_connection = TrackerConnection(url=parsed_tracker_url,
                                                       sock=sock,
                                                       connection_id=response.connection_id)
                tracker_connections.append(tracker_connection)
            except (ConnectionException, InvalidURLException) as exc:
                logger.info(exc.args[0])

        return tracker_connections

    def _send_announces(self, tracker_connections: [TrackerConnection]) -> {TrackerConnection: AnnounceResponse}:
        tracker_announce_responses = {}
        for tracker_connection in tracker_connections:
            # sending initial announce request
                announce_response = tracker_connection.announce(client_id=self.id,
                                                                torrent=self.torrent,
                                                                left=self.torrent.info.size(),
                                                                downloaded=0,
                                                                uploaded=0,
                                                                event=0)
                tracker_announce_responses[tracker_connection] = announce_response
        return tracker_announce_responses

    @staticmethod
    def _get_best_tracker(tracker_peers: {TrackerConnection: [PeerConnection]}) -> TrackerConnection:
        # we assume that tracker_peers is always not empty
        best_tracker = None
        for tracker in tracker_peers.keys():
            if not best_tracker or len(tracker_peers[tracker]) > len(tracker_peers[best_tracker]):
                best_tracker = tracker
        best_tracker.peers = tracker_peers[best_tracker]
        return best_tracker

    @staticmethod
    def _get_tracker_peers(tracker_announce_responses: {TrackerConnection: AnnounceResponse}) -> {TrackerConnection: List}:
        tracker_peer_connections = {}

        for tracker in tracker_announce_responses.keys():
            announce_response = tracker_announce_responses[tracker]
            logger.info(f"Available peers: {announce_response.peers}")

            connectable_peers = []
            # connecting to each peer, who has the data
            for peer_host, peer_port in announce_response.peers:
                sock = TCPSocket(dest_host=peer_host,
                                 dest_port=peer_port,
                                 timeout=3)
                logger.info(f"Connecting to peer on {peer_host}")

                try:
                    sock.connect()
                except ConnectionException as exc:
                    logger.info(exc.args[0])
                else:
                    logger.info("Connected!")
                    PeerConnection(sock=sock)
                    connectable_peers.append(PeerConnection)

            tracker_peer_connections[tracker] = connectable_peers

        return tracker_peer_connections

    @staticmethod
    def _send_connect(sock: UDPSocket, request: bytes, parsed_tracker_url: ParseResult) -> bool:
        try:
            sock.send(request,
                      dest_host=parsed_tracker_url.hostname,
                      dest_port=parsed_tracker_url.port)
        except socket.gaierror:
            # hostname is invalid
            raise InvalidURLException(f"{parsed_tracker_url.geturl()} is invalid")
        return True

    @staticmethod
    def _receive_connect(sock: UDPSocket, transaction_id: int, parsed_tracker_url: ParseResult) -> ConnectResponse:
        try:
            response = ConnectResponse(sock.receive(1024))
        except TimeoutError:
            raise ConnectionException(f"Connection to {parsed_tracker_url.geturl()} timed out")
        else:
            if response.transaction_id != transaction_id:
                raise InvalidTransactionException(f"Invalid transaction id sent by {parsed_tracker_url.geturl()}")
            else:
                logger.info(f"Response from {parsed_tracker_url.geturl()}: {response}")
                return response
