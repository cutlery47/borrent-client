from borrent_parser.decoder import Decoder

from src.entities.torrent.torrent import TorrentInfo, Torrent
from src.entities.torrent.multifile import TorrentMultiFileInfo, FileInfo
from src.entities.torrent.singlefile import TorrentSingleFileInfo

from dataclasses import asdict

class TorrentInfoConverter:

    @staticmethod
    def into_dict(info: TorrentInfo) -> dict:
        info_dict = asdict(info)
        # replacing underscore in the key in order to match the initial bencode
        info_dict['piece length'] = info_dict.pop('piece_length')
        return info_dict

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

class TorrentConverter:

    @staticmethod
    def into_dict(torrent: Torrent) -> dict:
        info_dict = TorrentInfoConverter.into_dict(torrent.info)
        torrent_dict = asdict(torrent)
        torrent_dict['info'] = info_dict
        # replacing underscore in the key in order to match the initial bencode
        torrent_dict['announce list'] = torrent_dict.pop('announce_list')
        torrent_dict['creation date'] = torrent_dict.pop('creation_date')
        torrent_dict['created by'] = torrent_dict.pop('created_by')
        return torrent_dict

    @staticmethod
    def into_torrent(bin_meta: bytes) -> Torrent:
        decoder = Decoder()
        decoded_meta = decoder.decode(bin_meta)
        print(decoded_meta)

        info_dict: dict = decoded_meta['info']
        info = TorrentInfoConverter.into_info(info_dict)

        torrent = Torrent(
            info=info,
            announce=decoded_meta.get('announce'),
            announce_list=decoded_meta.get('announce list'),
            creation_date=decoded_meta.get('creation date'),
            comment=decoded_meta.get('comment'),
            created_by=decoded_meta.get('created by'),
            encoding=decoded_meta.get('encoding')
        )
        return torrent
