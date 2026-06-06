"""
用于睡眠脑电波原始数据的提取
"""
import numpy as np
import pandas as pd
import os
import random
from scipy.signal import welch
from datetime import datetime
from pathlib import Path


class RawDataExtract(object):

    def __init__(self):
        self.raw_data_path = str(Path(__file__).parent.parent / "raw_data" / "ecg_chy1.xls")

    def split_raw_eeg(self, eeg_data):
        # 采样率
        fs = 100
        # 30s 数据的长度
        segment_length = fs * 30

        # 分段计算 PSD
        num_segments = len(eeg_data) // segment_length
        # print(len(eeg_data))
        eeg_list = []
        for i in range(num_segments):
            start = i * segment_length
            end = (i + 1) * segment_length
            segment = eeg_data[start:end]
            eeg_list.append([segment])
        return eeg_list

    def data_extract(self):
        # 读取 Excel 文件
        df = pd.read_excel(self.raw_data_path, header=None)
        # 假设数据在第一列
        eeg_data = df.iloc[:, 1].values
        # 尝试将数据转换为数值类型
        eeg_data = pd.to_numeric(eeg_data, downcast='float', errors='coerce')
        # 去除 NaN 值
        eeg_data = eeg_data[~np.isnan(eeg_data)]
        # 把原始的数据转化EDF的数据集
        eeg_30 = (((eeg_data * 1.8046e-05 * 2.048) / 8388608) - 1.55 * 1.8046e-05) / (3798.957 * 0.0001)

        














