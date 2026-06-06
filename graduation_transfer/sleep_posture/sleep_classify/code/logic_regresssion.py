import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import matplotlib as mpl
from tqdm import tqdm
import os

# 1. 加载相关的数据
path = "../after_process_data/after_process_data/"
# 获取所有的不是motion得excel的文件
execl_files = [f for f in os.listdir(path) if not f.endswith("motion.xlsx")][0:50]
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
Y = new_df.iloc[:, -1]

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.25, random_state=5)

model = LogisticRegression()
"""
penalty='l2', 过拟合解决参数,l1正则或者l2正则 {'l1', 'l2', 'elasticnet', 'none'}, default='l2'；'newton-cg'、'sag' 和 'lbfgs' 求解器仅支持 l2 惩罚。'elasticnet' 仅由 'saga' 求解器支持。如果为“无”（不受 liblinear 求解器支持），则不应用正则化。
dual=False, 
tol=1e-4, 梯度下降停止条件
C=1.0, 正则化强度的倒数；必须是正浮点数。较小的值指定更大的正则化
fit_intercept=True, 
intercept_scaling=1, 
class_weight=None, 类别权重，有助于解决数据类别不均衡的问题
random_state=None, 
solver='liblinear',  参数优化方式，当penalty为l1的时候，参数只能是：liblinear(坐标轴下降法)；当penalty为l2的时候，参数可以是：lbfgs(拟牛顿法)、newton-cg(牛顿法变种)，seg(minibatch),维度<10000时，lbfgs法比较好， 维度>10000时， cg法比较好，显卡计算的时候，lbfgs和cg都比seg快【nlbfgs和cg都是关于目标函数的二阶泰勒展开】
max_iter=100, 最多的迭代次数
multi_class='ovr', 分类方式参数；参数可选: ovr(默认)、multinomial；这两种方式在二元分类问题中，效果是一样的；在多元分类问题中，效果不一样；ovr: one-vs-rest， 对于多元分类的问题，先将其看做二元分类，分类完成后，再迭代对其中一类继续进行二元分类；multinomial: many-vs-many（MVM）,即Softmax分类效果
verbose=0, 
warm_start=False, 
n_jobs=1
## Logistic回归是一种分类算法，不能应用于回归中(也即是说对于传入模型的y值来讲，不能是float类型，必须是int类型)
"""
# logis.fit(x_train, y_train)
# train_score = logis.score(x_train, y_train)
# test_score = logis.score(x_test, y_test)
# y_test_hat = logis.predict(x_test)
# print(f"test_score:{test_score}")
# print(f"train_score:{train_score}")

param_grid = {
    'penalty': ['l1', 'l2'],
    'C': np.logspace(-4, 4, 20),
    'solver': ['liblinear']
}

grid_search = GridSearchCV(model, param_grid, cv=5, verbose=1, n_jobs=-1)
grid_search.fit(x_train, y_train)

print("Best parameters found: ", grid_search.best_params_)
print("Best cross-validation score: {:.2f}".format(grid_search.best_score_))
# 使用最佳参数的模型
best_model = grid_search.best_estimator_

y_pred = best_model.predict(x_test)
print(classification_report(y_test, y_pred))
