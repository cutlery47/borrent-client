from src.client.converter import MetaInfoConverter

from src.entities.torrent.metainfo import MetaInfo, Info
from src.entities.torrent.multifile import MultiFileInfo, FileInfo
from src.entities.torrent.singlefile import SingleFileInfo

class BorrentClient:

    def __init__(self, path: str):
        self.path = path

    def exec(self):
        with open(self.path, "rb") as file:
            bin_meta = file.read()

        converter = MetaInfoConverter()
        meta = converter.convert(bin_meta)


