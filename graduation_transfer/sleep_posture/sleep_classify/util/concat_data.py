"""
主要将所有的孕妇的数据合并为一个xlsx的文件
"""
import os
import pandas as pd
from tqdm import tqdm
# 数据的主要目录
path = "../after_process_data/after_process_data/"
# 获取所有的不是motion得excel的文件
execl_files = [f for f in os.listdir(path) if not f.endswith("motion.xlsx")]
# 创建一个进度条
progress_bar = tqdm(total=len(execl_files), desc="progress file")
# 创建一个空的DataFrame的数据
dataframes = list()
for file_name in execl_files:
    file_path = os.path.join(path, file_name)
    df = pd.read_excel(file_path, header=None, nrows=20000)
    if file_name.endswith("left.xlsx"):
        # 表示左躺睡觉
        df["label"] = "left"
    elif file_name.endswith("m.xlsx"):
        # 表示正常睡觉
        df["label"] = "mid"
    else:
        # 表示右躺睡觉
        df["label"] = "right"
    # 当前的文件追加到all_data中
    dataframes.append(df)
    progress_bar.update(1)

progress_bar.close()  # 完成时关闭进度条
all_data = pd.concat(dataframes, ignore_index=False)
column_names = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'feature6', "label"]
# 将当前的文件保存到本地
save_file = "./save_execl.xlsx"
all_data.to_excel(save_file, index=False)


