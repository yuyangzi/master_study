"""
聚类的相关问题的处理
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from tqdm import tqdm
from sklearn.metrics import accuracy_score
from sklearn.metrics import adjusted_rand_score
import os

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

new_df.sort_values(by="label", ascending=True, inplace=True)
# 3. 根据需求获取最原始的特征属性矩阵X和目标属性Y
X = np.array(new_df.iloc[:, :-1])
# # print(X.shape)
y_true = np.array(new_df.iloc[:, -1])


# 计算每个标签组的中心点
unique_labels = np.unique(y_true)
centroids = np.array([np.mean(X[y_true == label], axis=0) for label in unique_labels])

# 运行 K-means 算法，聚类数与标签数相同
kmeans = KMeans(n_clusters=len(unique_labels), init=centroids, n_init=1, random_state=0)
kmeans.fit(X)
y_pred = kmeans.predict(X)

# 使用调整兰德指数评估标签准确性
ari = adjusted_rand_score(y_true, y_pred)
print(f"Adjusted Rand Index: {ari}")


# sses = []
# S = []
# for K in range(2, 10):
#     kmeans = KMeans(n_clusters=K)
#     kmeans.fit(X)
#     inertia = kmeans.inertia_
#     sses.append(inertia)
#     labels = kmeans.labels_
#     s = silhouette_score(X, labels)
#     # print(s*100)
#     S.append(s)
# plt.figure(num=1)
# plt.plot(range(2, 10), sses)
# plt.figure(num=2)
# plt.plot(range(2, 10), S)
# plt.show()