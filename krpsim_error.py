class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)

class InputError(CustomError):
    pass

class OutputError(CustomError):
    pass

class ErrorInput(CustomError):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class ErrorOutput(CustomError):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class KRPError(CustomError):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
