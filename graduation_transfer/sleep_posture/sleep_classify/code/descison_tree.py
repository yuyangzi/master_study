"""
使用决策树对睡眠数据进行分类
"""
import warnings
import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import auc, roc_curve, classification_report
import os
from tqdm import tqdm

# 1. 加载相关的数据
path = "../after_process_data/after_process_data/"
# 获取所有的不是motion得excel的文件
execl_files = [f for f in os.listdir(path) if not f.endswith("motion.xlsx")]
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

# 四、数据分割(将数据分割为训练数据和测试数据)
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.1, random_state=28)
print("训练数据X的格式:{}, 以及数据类型:{}".format(x_train.shape, type(x_train)))
print("测试数据X的格式:{}".format(x_test.shape))
print("训练数据Y的数据类型:{}".format(type(y_train)))
print("Y的取值范围:{}".format(np.unique(Y)))


# 六、模型对象的构建
"""
def __init__(self,
             criterion="gini",
             splitter="best",
             max_depth=None,
             min_samples_split=2,
             min_samples_leaf=1,
             min_weight_fraction_leaf=0.,
             max_features=None,
             random_state=None,
             max_leaf_nodes=None,
             min_impurity_decrease=0.,
             min_impurity_split=None,
             class_weight=None,
             presort=False)
    criterion: 给定决策树构建过程中的纯度的衡量指标，可选值: gini、entropy， 默认gini
    splitter：给定选择特征属性的方式，best指最优选择，random指随机选择(局部最优)
    max_features：当splitter参数设置为random的有效，是给定随机选择的局部区域有多大。
    max_depth：剪枝参数，用于限制最终的决策树的深度，默认为None，表示不限制
    min_samples_split=2：剪枝参数，给定当数据集中的样本数目大于等于该值的时候，允许对当前数据集进行分裂；如果低于该值，那么不允许继续分裂。
    min_samples_leaf=1, 剪枝参数，要求叶子节点中的样本数目至少为该值。
    class_weight：给定目标属性中各个类别的权重系数。
"""
# 用于限制决策树的深度
algo = DecisionTreeClassifier(max_depth=7, min_samples_split=6, criterion="entropy")

# 七. 模型的训练
algo.fit(x_train, y_train)

# 画图
# 对于三个类别分开计算auc和roc的值
y_predict_proba = algo.predict_proba(x_train)
# print(y_predict_proba)
# 针对于类别1
y1_true = (y_train == 0).astype(np.int32)
y1_score = y_predict_proba[:, 0]


fpr1, tpr1, _ = roc_curve(y1_true, y1_score)
auc1 = auc(fpr1, tpr1)
# 针对于类别2
y2_true = (y_train == 1).astype(np.int32)
y2_score = y_predict_proba[:, 1]

fpr2, tpr2, _ = roc_curve(y2_true, y2_score)
auc2 = auc(fpr2, tpr2)
# 针对于类别3
y3_true = (y_train == 2).astype(np.int32)
y3_score = y_predict_proba[:, 2]

fpr3, tpr3, _ = roc_curve(y3_true, y3_score)
auc3 = auc(fpr3, tpr3)
print(f"auc:{(auc1, auc2, auc3)}")
# print((auc1, auc2))

plt.plot(fpr1, tpr1, 'r-o', label="ROC curve(area=%0.2f)" % auc1)
plt.plot(fpr2, tpr2, 'g-o', label="ROC curve(area=%0.2f)" % auc2)
plt.plot(fpr3, tpr3, 'b-o', label="ROC curve(area=%0.2f)" % auc3)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic example')
plt.legend(loc="lower right")
plt.show()