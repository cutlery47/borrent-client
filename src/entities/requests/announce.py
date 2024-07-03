from dataclasses import dataclass, asdict
import struct
import socket

FIXED_LENGTH = 20
PEER_DATA_LENGTH = 6


@dataclass
class AnnounceRequest:
    connection_id: int
    action: int
    info_hash: bytes
    transaction_id: int
    peer_id: bytes
    downloaded: int
    left: int
    uploaded: int
    event: int
    ip_address: int
    key: int
    num_want: int
    port: int

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_binary(self):
        return struct.pack('!qii20s20sqqqiiiih',
                           self.connection_id,
                           self.action,
                           self.transaction_id,
                           self.info_hash,
                           self.peer_id,
                           self.downloaded,
                           self.left,
                           self.uploaded,
                           self.event,
                           self.ip_address,
                           self.key,
                           self.num_want,
                           self.port)

@dataclass
class AnnounceResponse:
    action: int
    transaction_id: int
    interval: int
    leechers: int
    seeders: int
    peers: list

    def __init__(self, response: bytes):
        peers_data_length = len(response) - FIXED_LENGTH
        peers_amount = peers_data_length // PEER_DATA_LENGTH

        format = '!iiiii' + peers_amount * 'ih'
        response_data = struct.unpack(format, response)

        self.action = response_data[0]
        self.transaction_id = response_data[1]
        self.interval = response_data[2]
        self.leechers = response_data[3]
        self.seeders = response_data[4]
        self.peers = []
        for i in range(5, len(response_data), 2):
            # for each peer, store its ip and port
            self.peers.append((socket.inet_ntoa(struct.pack('!i', response_data[i])), response_data[i + 1]))
