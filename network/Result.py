import torch
class Result:
    label_name : str
    score : torch.Tensor
    is_tired : bool
    time : float

    def __init__(self,label,score,tired,time):
        self.label_name = label
        self.score = score
        self.is_tired = tired
        self.time = time
