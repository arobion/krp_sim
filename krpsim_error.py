class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ErrorInput(CustomError):
    pass

class ErrorOutput(CustomError):
    pass

class KRPError(CustomError):
    pass
