class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InputError(CustomError):
    pass


class OutputError(CustomError):
    pass


class KRPError(CustomError):
    pass
