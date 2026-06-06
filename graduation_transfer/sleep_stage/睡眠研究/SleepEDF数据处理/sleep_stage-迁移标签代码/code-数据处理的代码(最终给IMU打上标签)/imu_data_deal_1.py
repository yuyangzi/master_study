"""
用于处理imu的数据
"""
import pandas as pd
import numpy as np
from pathlib import Path


class IMUDataToCSV(object):

    def __init__(self):
        self.file_path = str(Path(__file__).parent.parent / "rawdata" / "gjx" / "")
        self.save_path = str(Path(__file__).parent.parent / "EEG_data" / "imu_gjx" / "")

    def deal_eeg_data(self):
        for i in range(2, 3):
            file_path = self.file_path + f"imu_gjx_0715.xls"
            save_path = self.save_path + f"imu_gjx_0715.csv"

            print(f"file_path:{file_path}")
            print(f"save_path:{save_path}")
            # 根据您的描述：第一列时间戳，第二列信号数据
            file2 = pd.read_csv(file_path, sep='\t', header=None)
            print(file2.head())

            # 给列名
            file2.columns = ['time_stamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz']

            # 保存为标准CSV文件
            file2.to_csv(save_path, index=False)


if __name__ == '__main__':
    IMUDataToCSV().deal_eeg_data()