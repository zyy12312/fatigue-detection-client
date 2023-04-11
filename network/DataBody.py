import Error
from network.Result import Result

class DataBody:
    error : Error
    res : list[Result]
    is_tired : bool
    time : float
    def __init__(self,error:Error,res:list[Result],tired:bool,time:float):
        self.error = error
        self.res = res
        self.is_tired = tired
        self.time = time