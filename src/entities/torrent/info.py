from dataclasses import dataclass
from src.entities.torrent.torrent import TorrentInfo

@dataclass
class FileInfo:
    """
    Attributes:
        length (int): Length of the file in bytes.
        path (list): A list containing one or more string elements that together represent the path and filename.
        md5sum (str): A 32-character hexadecimal string corresponding to the MD5 sum of the file.
    """
    length: int
    path: list[str]
    md5sum: str

@dataclass
class TorrentMultiFileInfo(TorrentInfo):
    """
    Attributes:
        piece_length (int): Number of bytes in each piece.
        pieces (bytes): String consisting of the concatenation of all 20-byte SHA1 hash values.
        private (int): (Optional). If it is set to "1", the client MUST publish its presence to get other peers.
        name (str): The name of the directory in which to store all the files.
        files (list): A list of dictionaries.
    """
    piece_length: int
    pieces: bytes
    private: int
    name: str
    files: [FileInfo]

    def size(self):
        size = 0
        for file in self.files:
            size += file.length
        return size

@dataclass
class TorrentSingleFileInfo(TorrentInfo):
    """
    Attributes:
        piece_length (int): Number of bytes in each piece.
        pieces (bytes): String consisting of the concatenation of all 20-byte SHA1 hash values.
        private (int): (Optional). If it is set to "1", the client MUST publish its presence to get other peers.
        name (str): The file name
        length (int): Length of the file in bytes
        md5sum (str): A 32-character hexadecimal string corresponding to the MD5 sum of the file.
    """
    piece_length: int
    pieces: bytes
    private: int
    name: str
    length: int
    md5sum: str

    def size(self):
        return self.length