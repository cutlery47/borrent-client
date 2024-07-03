from dataclasses import dataclass, asdict
import struct
import random

@dataclass
class ConnectRequest:
    transaction_id: int
    protocol_id: int = 0x41727101980  # magic constant
    action: int = 0  # connect

    def __init__(self, transaction_id: int):
        self.transaction_id = transaction_id

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_binary(self) -> bytes:
        return struct.pack('!qii', self.protocol_id, self.action, self.transaction_id)

@dataclass
class ConnectResponse:
    action: int
    transaction_id: int
    connection_id: int

    def __init__(self, response: bytes):
        response_data = struct.unpack('!iiq', response)
        self.action = response_data[0]
        self.transaction_id = response_data[1]
        self.connection_id = response_data[2]

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}
