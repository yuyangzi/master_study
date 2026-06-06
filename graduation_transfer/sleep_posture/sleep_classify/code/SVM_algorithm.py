"""
向量机进行处理
"""
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import matplotlib.pyplot as plt
import time
import sys
import warnings

warnings.filterwarnings('ignore')
import os

# 1. 加载相关的数据
path = "../after_process_data/after_process_data/"
# 获取所有的不是motion得excel的文件
execl_files = [f for f in os.listdir(path) if not f.endswith("motion.xlsx")][:15]
# 创建一个进度条
progress_bar = tqdm(total=len(execl_files), desc="progress file")
column_names = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'feature6', "label"]
# 创建一个空的DataFrame的数据
dataframes = list()
# 2 数据处理
for file_name in execl_files:
    file_path = os.path.join(path, file_name)
    df = pd.read_excel(file_path, header=None)
    if file_name.endswith("left.xlsx"):
        # 表示左躺睡觉
        df["label"] = 0
    elif file_name.endswith("m.xlsx"):
        # 表示正常睡觉
        df["label"] = 1
    else:
        # 表示右躺睡觉
        df["label"] = 2
    # 当前的文件追加到all_data中
    dataframes.append(df)
    progress_bar.update(1)
progress_bar.close()  # 完成时关闭进度条
new_df = pd.concat(dataframes, ignore_index=False)
new_df.label = new_df.label.astype(np.int32)

# 3. 根据需求获取最原始的特征属性矩阵X和目标属性Y
X = new_df.iloc[:, :-1]
# print(X.shape)
Y = new_df.iloc[:, -1]

xtrain, xtest, ytrain, ytest = train_test_split(X, Y, test_size=0.3, random_state=10)
# print(xtrain)
rbf = SVC(kernel='rbf', C=5, gamma=0.1)
linears = SVC(kernel='linear', C=5)
polys = SVC(kernel='poly', gamma=0.1, coef0=0.5, degree=4, C=5)
sigmoids = SVC(kernel='sigmoid', gamma=0.01, coef0=0.5, C=5, decision_function_shape='ovr')

# model.append([rbf,linears,polys,sigmoids,precomputeds])
# print(model)
models = np.array([rbf, linears, polys, sigmoids])
# sys.exit(0)
times = []
train_scores = []
test_scores = []

for model in models:
    state = time.time()
    model.fit(xtrain, ytrain)
    end = time.time()
    train_score = model.score(xtrain, ytrain)
    test_score = model.score(xtest, ytest)
    times.append(end - state)
    train_scores.append(train_score)
    test_scores.append(test_score)

print('运行所需时间：', times)
print('训练集分数：', train_scores)
print('测试集分数：', test_scores)

plt.figure(num=1)
plt.plot(['01rbf', '02linear', '03poly', '04sigmoid'], train_scores, 'r', label='trainscore')
plt.plot(['01rbf', '02linear', '03poly', '04sigmoid'], test_scores, 'b', label='testscore')
plt.figure(num=2)
plt.plot(['01rbf', '02linear', '03poly', '04sigmoid'], times, 'g', label='time')
plt.show()