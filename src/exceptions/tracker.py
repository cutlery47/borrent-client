class TrackerException(Exception):
    pass

class UnavailableTrackersException(TrackerException):

    def __init__(self, message="No trackers are available at the moment"):
        super().__init__(message)

class InvalidTransactionException(TrackerException):

    def __init__(self, message="Transaction id's do not match"):
        super().__init__(message)

class InvalidURLException(TrackerException):

    def __init__(self, message="Tracker url can't be accessed"):
        super().__init__(message)