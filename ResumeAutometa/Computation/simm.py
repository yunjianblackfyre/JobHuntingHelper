# -*- coding:utf-8 -*-
import numpy as np
from numpy import linalg as LA


def simm(vector_a, vector_b):
    # 需要用词向量余弦距离计算
    dot_product = np.dot(vector_a, vector_b)
    norm_product = LA.norm(vector_a) * LA.norm(vector_b)
    simm = (dot_product / norm_product)
    return simm