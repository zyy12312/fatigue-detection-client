import Error
from network.Result import Result

class DataBody:
    error : Error
    res : list[Result]
    def __init__(self,error:Error,res:list[Result],tired:bool):
        self.error = error
        self.res = res
