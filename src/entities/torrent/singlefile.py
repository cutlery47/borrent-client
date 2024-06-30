from dataclasses import dataclass
from src.entities.torrent.metainfo import Info

@dataclass
class SingleFileInfo(Info):
    """
    Attributes:
        name (str): The file name
        length (int): Length of the file in bytes
        md5sum (str): A 32-character hexadecimal string corresponding to the MD5 sum of the file.
    """
    name: str
    length: int
    md5sum: str


