class CustomError(Exception):
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
