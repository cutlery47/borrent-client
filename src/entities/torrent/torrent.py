from dataclasses import dataclass, asdict

from src.entities.torrent.torrent_info import TorrentInfo, TorrentInfoConverter

from bcoding import bdecode


@dataclass
class TorrentStats:
    info_hash: bytes = b''
    leechers: int = 0
    seeders: int = 0
    left: int = 0
    downloaded: int = 0
    uploaded: int = 0
    connection_id: int = 0


@dataclass
class Torrent:
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
    info: TorrentInfo
    announce: str
    announce_list: list
    creation_date: str
    comment: str
    created_by: str
    encoding: str


class TorrentConverter:

    @staticmethod
    def into_dict(torrent: Torrent) -> dict:
        info_dict = TorrentInfoConverter.into_dict(torrent.info)
        torrent_dict = asdict(torrent)
        torrent_dict['info'] = info_dict
        # replacing underscore in the key in order to match the initial bencode
        torrent_dict['announce-list'] = torrent_dict.pop('announce_list')
        torrent_dict['creation date'] = torrent_dict.pop('creation_date')
        torrent_dict['created by'] = torrent_dict.pop('created_by')

        return {k: v for k, v in torrent_dict.items() if v is not None}

    @staticmethod
    def into_torrent(bin_torrent: bytes) -> Torrent:
        decoded_torrent = bdecode(bin_torrent)

        info_dict: dict = decoded_torrent['info']
        info = TorrentInfoConverter.into_info(info_dict)

        torrent = Torrent(
            info=info,
            announce=decoded_torrent.get('announce'),
            announce_list=decoded_torrent.get('announce-list'),
            creation_date=decoded_torrent.get('creation date'),
            comment=decoded_torrent.get('comment'),
            created_by=decoded_torrent.get('created by'),
            encoding=decoded_torrent.get('encoding')
        )
        return torrent



