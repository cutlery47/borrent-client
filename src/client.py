from src.entities.torrent.torrent import Torrent, TorrentConverter

from src.entities.requests.connect import ConnectRequest, ConnectResponse
from src.entities.requests.announce import AnnounceResponse

from src.networking.sockets import UDPSocket, TCPSocket
from src.networking.connections import TrackerConnection, PeerConnection

from src.exceptions.tracker import (InvalidTransactionException, InvalidURLException)
from src.exceptions.socket import ConnectionException

from loguru import logger
from typing import List
from urllib.parse import urlparse, ParseResult
import random
import socket
import asyncio

TRANSACTION_ID = 1337

class BorrentClient:

    def __init__(self, path: str):

        # reading the torrent file and converting it into Torrent instance right away
        with open(path, "rb") as file:
            self.torrent = TorrentConverter.into_torrent(file.read())

        # id, which is used on each announce request
        self.id = "-XD0001-" + "".join([str(random.randint(0, 9)) for _ in range(12)])

    async def start(self):
        """
        Initiating the client:
        1) Choosing the best tracker to download from
            1.1) Collecting all the trackers for the .torrent file
            1.2) Sending Announce Requests to all available ones
            1.3) Each Announce Response contains a list of peers, connected to it.
                 For download purposes the best tracker is the one, which has the most connected peers.
                 So we just parse each Announce Response and select the tracker with the most peers as the best one
        2) Connecting to peers
        3) Downloading from peers
        """

        # collecting all available trackers
        tracker_connections = await self._connect_to_trackers(self.torrent)

        return

        # announcing ourselves to each of the collected trackers
        tracker_announce_responses = self._send_announces(tracker_connections)

        # creating a mapping: tracker => list of peers
        tracker_peers = self._get_tracker_peers(tracker_announce_responses)

        # finding the best tracker
        tracker = self._get_best_tracker(tracker_peers)

    async def _connect_to_trackers(self, torrent: Torrent) -> [TrackerConnection]:
        """
        Provided a .torrent file metadata, we are trying to establish tracker connections.
        A tracker can be accessed by its url address, which is stored in the "announce-list" header.

        Args:
            torrent: .torrent file metainfo in form of a dataclass instance

        Returns:
            A list of tracker connections
        """

        # list of all established connections
        tracker_connections = []

        # creating a distinct udp socket for each tracker connection
        sock = UDPSocket(timeout=1, blocking=True)

        # creating connect request
        connect_request = ConnectRequest(TRANSACTION_ID)

        tasks = []

        # searching for any available trackers of the torrent
        for tracker_url in torrent.announce_list:
            task = asyncio.create_task(self._get_tracker_connection(tracker_url=tracker_url,
                                                                    connect_request=connect_request,
                                                                    sock=sock))
            tasks.append(task)

        res = await asyncio.gather(*tasks)
        return tracker_connections



    def _send_announces(self, tracker_connections: [TrackerConnection]) -> {TrackerConnection: AnnounceResponse}:
        """
        Provided a list of tracker connections, send an Announce Request for each connection

        Args:
            tracker_connections: List of all established tracker connections

        Returns:
            Mapping of TrackerConnections to their corresponding AnnounceResponses
        """

        # the resulting mapping
        tracker_announce_responses = {}

        for tracker_connection in tracker_connections:
            # sending initial announce request
            announce_response = tracker_connection.announce(client_id=self.id,
                                                            torrent=self.torrent,
                                                            left=self.torrent.info.size(),
                                                            downloaded=0,
                                                            uploaded=0,
                                                            event=0)
            # Map TrackerConnection => AnnounceResponse
            tracker_announce_responses[tracker_connection] = announce_response

        return tracker_announce_responses

    async def _get_tracker_connection(self,
                                      tracker_url: str,
                                      connect_request: ConnectRequest,
                                      sock: UDPSocket
                                      ) -> TrackerConnection | None:
        logger.info(f"Trying out {tracker_url}")

        # check, if url can be parsed in the first place :)
        parsed_tracker_url = urlparse(tracker_url[0])
        if not parsed_tracker_url.port:
            logger.info(f"Connection with {tracker_url} can't be established: port was not provided")
            return

        try:
            # sending connect request and receiving response
            response = self._send_connect(request=connect_request, sock=sock, parsed_tracker_url=parsed_tracker_url)

            # creating connection object, using connection_id from response
            tracker_connection = TrackerConnection(url=parsed_tracker_url,
                                                   sock=sock,
                                                   connection_id=response.connection_id)

            return tracker_connection
        except (ConnectionException, InvalidURLException) as exc:
            logger.info(exc.args[0])


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
    def _get_best_tracker(tracker_peers: {TrackerConnection: [PeerConnection]}) -> TrackerConnection:
        # we assume that tracker_peers is always not empty
        best_tracker = None
        for tracker in tracker_peers.keys():
            if not best_tracker or len(tracker_peers[tracker]) > len(tracker_peers[best_tracker]):
                best_tracker = tracker
        best_tracker.peers = tracker_peers[best_tracker]
        return best_tracker


    @staticmethod
    def _send_connect(request: ConnectRequest, sock: UDPSocket, parsed_tracker_url: ParseResult) -> ConnectResponse:
        """
        Method basically consists of 2 parts:
        1) Sending connect request
        2) Receiving connect request
        Args:
            sock: UDPSock, from which the request will be sent
            parsed_tracker_url: Object, containing all the data about demanded url

        Returns:
            ConnectResponse instance
        """

        # 1) Sending the request
        try:
            sock.send(data=request.to_binary(),
                      dest_host=parsed_tracker_url.hostname,
                      dest_port=parsed_tracker_url.port)
        except socket.gaierror:
            # hostname is invalid
            raise InvalidURLException(f"{parsed_tracker_url.geturl()} is invalid")

        # 2) Receiving response
        try:
            response = ConnectResponse(sock.receive(1024))
        except TimeoutError:
            # server didnt respond
            raise ConnectionException(f"Connection to {parsed_tracker_url.geturl()} timed out")
        except BlockingIOError:
            logger.info("xyu")
        else:
            # check that transaction id hasn't been spoofed
            if response.transaction_id != TRANSACTION_ID:
                raise InvalidTransactionException(f"Invalid transaction id sent by {parsed_tracker_url.geturl()}")
            else:
                return response
