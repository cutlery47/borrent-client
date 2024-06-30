from dataclasses import dataclass

@dataclass
class ResponsePeer:
    """
    Attributes:
        peer_id (str): Peer's self-selected ID.
        ip (str): Peer's IP address either IPv6 (hexed) or IPv4 (dotted quad) or DNS name.
        port (int): Peer's port number
    """
    peer_id: str
    ip: str
    port: int

@dataclass
class TrackerResponse:
    """
    Attributes:
        failure_reason (str): If present, then no other keys may be present.
        warning_message (str): (Optional) Similar to failure reason, but the response still gets processed normally.
        interval (int): Interval in seconds that the client should wait between sending regular requests to the tracker.
        min_interval: (Optional) Minimum announce interval. If present clients must not reannounce more frequently than this.
        tracker_id (str): A string that the client should send back on its next announcements.
        complete (int): number of peers with the entire file, i.e. seeders
        incomplete (int): Number of non-seeder peers, aka "leechers" (integer)
        peers_dict (list): (dictionary model) The value is a list of dictionaries, each with the following keys:
            peer id: peer's self-selected ID, as described above for the tracker request (string)
            ip: peer's IP address either IPv6 (hexed) or IPv4 (dotted quad) or DNS name (string)
            port: peer's port number (integer)
        peers_bin (str): (binary model) Instead of using the dictionary model described above, the peers value may be a string consisting of multiples of 6 bytes. First 4 bytes are the IP address and last 2 bytes are the port number.
    """
    failure_reason: str
    warning_message: str
    interval: int
    min_interval: int
    tracker_id: str
    complete: int
    incomplete: int
    peers_dict: list[ResponsePeer]
    peers_bin: str

