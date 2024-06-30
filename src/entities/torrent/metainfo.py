from dataclasses import dataclass


@dataclass
class Info:
    """
    Attributes:
        piece_length (int): Number of bytes in each piece.
        pieces (bytes): String consisting of the concatenation of all 20-byte SHA1 hash values.
        private (int): (Optional). If it is set to "1", the client MUST publish its presence to get other peers.
    """
    piece_length: int
    pieces: bytes
    private: int


@dataclass
class MetaInfo:
    """
    Attributes:
        info (Info): A dictionary that describes the file(s) of the torrent.
        announce (str): The announce URL of the tracker.
        announce_list (list): (Optional) This is an extension to the official specification, offering backwards-compatibility.
        creation_date (str): (Optional) The creation time of the torrent.
        comment: (Optional) Free-form textual comments of the author
        created_by: (Optional) Name and version of the program used to create the .torrent.
        encoding: (Optional) The encoding format used to generate the pieces part of the info dictionary.
    """
    info: Info
    announce: str
    announce_list: list
    creation_date: str
    comment: str
    created_by: str
    encoding: str
