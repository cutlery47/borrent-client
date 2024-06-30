from dataclasses import dataclass
from src.dataclasses.torrent.metainfo import Info

@dataclass
class File:
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
class MultiFile(Info):
    """
    Attributes:
        name (str): The name of the directory in which to store all the files.
        files (list): A list of dictionaries.
    """
    name: str
    files: list[File]
