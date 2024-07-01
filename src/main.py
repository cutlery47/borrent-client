from client.client import BorrentClient

import sys

if __name__ == "__main__":
    try:
        path = sys.argv[1]
    except IndexError as err:
        raise Exception("A path to the .torrent file should be provided")

    client = BorrentClient(path=path, host='0.0.0.0', port=6889)
    client.exec()
