from src.client import BorrentClient

import sys
import asyncio

if __name__ == "__main__":
    try:
        path = sys.argv[1]
    except IndexError as err:
        raise Exception("A path to the .torrent file should be provided")

    client = BorrentClient(path=path)
    asyncio.run(client.start())
