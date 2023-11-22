import numpy as np


class Transfrom:
    def __init__(self, trans_matrix=np.identity(4)):
        self.trans_matrix = trans_matrix

    def __call__(self, **post):
        # post["M_persp"] = post["M_persp"] @ self.trans_matrix
        return post
