from dataclasses import dataclass, asdict

from abc import ABC, abstractmethod

@dataclass
class TorrentInfo(ABC):

    @abstractmethod
    def size(self):
        raise NotImplementedError

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

class TorrentInfoConverter:

    @staticmethod
    def into_dict(info: TorrentInfo) -> dict:
        info_dict = asdict(info)
        # replacing underscore in the key in order to match the initial bencode
        info_dict['piece length'] = info_dict.pop('piece_length')

        # removing empty entries from the dict
        if info_dict.get('files'):
            info_dict['files'] = [{k: v for k, v in file.items() if v is not None} for file in info_dict['files']]

        return {k: v for k, v in info_dict.items() if v is not None}

    @staticmethod
    def into_info(info_dict: dict) -> TorrentInfo:
        # parsing the "info" nested dict
        name = info_dict.get('name')
        piece_length = info_dict.get('piece length')
        pieces = info_dict.get('pieces')
        private = info_dict.get('private')

        if info_dict.get('files'):
            # multifile torrent
            files = []
            for el in info_dict['files']:
                file = FileInfo(
                    length=el.get('length'),
                    path=el.get('path'),
                    md5sum=el.get('md5sum')
                )
                files.append(file)

            file_info = TorrentMultiFileInfo(
                files=files,
                name=name,
                piece_length=piece_length,
                pieces=pieces,
                private=private
            )
        else:
            # single file torrent
            file_info = TorrentSingleFileInfo(
                name=name,
                length=info_dict.get('length'),
                md5sum=info_dict.get('md5sum'),
                piece_length=piece_length,
                pieces=pieces,
                private=private
            )
        return file_info