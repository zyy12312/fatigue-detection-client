import torch
class Result:
    label_name : str
    score : torch.Tensor

    def __init__(self,label,score):
        self.label_name = label
        self.score = score
