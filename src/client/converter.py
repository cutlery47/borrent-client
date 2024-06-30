from borrent_parser.decoder import Decoder

from src.entities.torrent.metainfo import MetaInfo, Info
from src.entities.torrent.multifile import MultiFileInfo, FileInfo
from src.entities.torrent.singlefile import SingleFileInfo

class MetaInfoConverter:

    def convert(self, bin_meta: bytes) -> MetaInfo:
        decoder = Decoder()
        decoded_meta = decoder.decode(bin_meta)

        info_dict: dict = decoded_meta['info']
        info = self.get_info(info_dict)

        meta = MetaInfo(
            info=info,
            announce=decoded_meta.get('announce'),
            announce_list=decoded_meta.get('announce list'),
            creation_date=decoded_meta.get('creation date'),
            comment=decoded_meta.get('comment'),
            created_by=decoded_meta.get('created by'),
            encoding=decoded_meta.get('encoding')
        )

        return meta

    @staticmethod
    def get_info(info_dict: dict) -> Info:
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

            file_info = MultiFileInfo(
                files=files,
                name=name,
                piece_length=piece_length,
                pieces=pieces,
                private=private
            )
        else:
            # single file torrent
            file_info = SingleFileInfo(
                name=name,
                length=info_dict.get('length'),
                md5sum=info_dict.get('md5sum'),
                piece_length=piece_length,
                pieces=pieces,
                private=private
            )
        return file_info
