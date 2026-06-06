"""
主要是为了进行数据验证
"""
import joblib
import pandas as pd
import numpy as np

label_dict = {1: "left", 2: "mid", 3: "right"}

# 分别获取6000条以后得数据不带上标签
test = [
    [0.245098, -0.517695, -9.440458, -1.79375, 1.86375, 0.62125],  # left
    [0.243305, -0.521282, -9.433882,-1.86375, 1.81125, 0.58625],   # left
    [0.033477, -1.310378, -9.444044, -2.5725, 2.87875, 0.93625],   # mid
    [0.148852,-0.274988, -9.448827, -2.31875, 2.205, 0.79625]      # right
]
data = np.array(test)
columns = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'feature6']
self_test = pd.DataFrame(data, columns=columns)
kd_tree = joblib.load("../model/kd_tree.m")
print(kd_tree.predict(self_test))