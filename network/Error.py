class Error:
    code: int
    message: str
    def __init__(self,code,message):
        self.code = code
        self.message = message