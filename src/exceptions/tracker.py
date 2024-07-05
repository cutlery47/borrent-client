class ConnectionException(Exception):
    pass

class UnavailableTrackersException(ConnectionException):

    def __init__(self, message="No trackers are available at the moment"):
        super().__init__(message)

class InvalidTransactionException(ConnectionException):

    def __init__(self, message="Transaction id's do not match"):
        super().__init__(message)