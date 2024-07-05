class SocketException(Exception):
    pass


class ConnectionException(SocketException):

    def __init__(self, message="Couldn\'t not establish connection on socket"):
        super().__init__(message)
