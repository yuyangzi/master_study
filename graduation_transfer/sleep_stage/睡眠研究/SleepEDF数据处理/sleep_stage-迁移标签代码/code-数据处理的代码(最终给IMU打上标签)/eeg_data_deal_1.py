import pandas as pd
import numpy as np
from pathlib import Path


class RawDataToEEG:

    def __init__(self):
        self.file_path = str(Path(__file__).parent.parent / "rawdata" / "gjx" / "")
        self.save_path = str(Path(__file__).parent.parent / "EEG_data" / "gjx" / "")

    def deal_eeg_data(self):
        for i in range(2, 3):
            file_path = self.file_path + f"eeg_gjx_0715.xls"
            save_path = self.save_path + f"psg_eeg_gjx_0715.csv"

            print(f"file_path:{file_path}")
            print(f"save_path:{save_path}")
            # 根据您的描述：第一列时间戳，第二列信号数据
            df = pd.read_csv(file_path, header=None, names=['combined'])
            # 分割混合数据列
            split_data = df['combined'].str.split(r'\s+', expand=True, n=3)
            # 提取各个部分]
            df['时间'] = split_data[0]
            df['日期'] = split_data[1]
            df['信号数据'] = split_data[2]

            # 创建完整的日期时间列
            # 注意：日期格式为"2025/3/30"，时间格式为"3:48:59.945"
            df['time_stamp'] = df['日期'] + ' ' + df['时间']

            # 转换为标准datetime格式
            df['time_stamp'] = pd.to_datetime(df['time_stamp'], format='%Y/%m/%d %H:%M:%S.%f', errors='coerce')

            # 数据清洗：转换信号数据为数值类型
            df['clean_signal'] = pd.to_numeric(df['信号数据'], errors='coerce')
            df = df.dropna(subset=['clean_signal'])

            # ===================== 信号转换部分 =====================
            def convert_to_edf(raw_val):
                numerator = raw_val * 1.8046e-05 * 2.048
                numerator /= 8388608
                numerator -= 1.55 * 1.8046e-05
                denominator = 3798.957 * 0.0001
                return numerator / denominator

            # 应用转换函数
            df['edf_data'] = df['clean_signal'].apply(convert_to_edf)

            # 最终保留的列：完整时间戳、原始信号和转换后的EDF数据
            result = df[['time_stamp', 'edf_data']]

            # 检查结果
            print(f"处理完成！数据示例:{i}")
            print(result.head())
            # 可选：额外格式转换
            result.to_csv(save_path, index=False)


if __name__ == '__main__':
    RawDataToEEG().deal_eeg_data()
