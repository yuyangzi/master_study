"""
此处将对应的eeg的data转化为对应的可以训练的数据
"""
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
# from joblib import dump, load
# from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path


# config = {
#     "sequence_length": 10,  # 每个样本的时间步数（根据实际数据调整）
#     "input_size": 10,  # 每个时间步的特征数（mean到gamma_power共11个）
#     "hidden_size": 64,  # LSTM隐藏层维度
#     "num_layers": 2,  # LSTM堆叠层数
#     "num_classes": 4,  # 睡眠阶段类别数
#     "batch_size": 32,
#     "dropout": 0.3,
#     "learning_rate": 0.001,
#     "num_epochs": 50
# }

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def compute_psd_with_timestamps(eeg_data, timestamps, fs=100):
    """
    根据图二代码处理EEG数据，同时保留时间信息
    参数：
        eeg_data: EEG数据数组
        timestamps: 对应的时间戳数组
        fs: 采样率 (默认100Hz)
    """
    # 30秒数据的长度
    segment_length = fs * 30

    # 分段计算PSD
    num_segments = len(eeg_data) // segment_length

    band_power_list = []
    timestamp_info = []

    for i in range(num_segments):
        start_idx = i * segment_length
        end_idx = (i + 1) * segment_length - 1

        segment = eeg_data[start_idx:end_idx + 1]
        segment_timestamps = timestamps[start_idx:end_idx + 1]

        # 提取时间信息
        start_time = segment_timestamps.iloc[0]
        end_time = segment_timestamps.iloc[-1]

        # 检查时间差是否符合30秒周期
        time_diff = (end_time - start_time).total_seconds()
        if abs(time_diff - 30) > 1:  # 允许1秒误差
            continue  # 跳过不符合要求的段

        # 计算PSD
        frequencies, psd = signal.welch(segment, fs, nperseg=segment_length)

        # 提取各波段功率
        band_power = {}
        # 添加时域特征
        # mean = np.mean(segment)
        # std = np.std(segment)
        # max_val = np.max(segment)
        # min_val = np.min(segment)
        # energy = np.sum(segment ** 2)
        band_power['mean'] = np.mean(segment)
        band_power['std'] = np.std(segment)
        band_power['max'] = np.max(segment)
        band_power['min'] = np.min(segment)
        band_power['energy'] = np.sum(segment ** 2)
        # 添加频域信号
        # delta_power = np.sum(psd[(frequencies >= 0.5) & (frequencies < 4)])
        # theta_power = np.sum(psd[(frequencies >= 4) & (frequencies < 8)])
        # alpha_power = np.sum(psd[(frequencies >= 8) & (frequencies < 12)])
        # beta_power = np.sum(psd[(frequencies >= 12) & (frequencies < 30)])
        # gamma_powder = np.sum(psd[(frequencies >= 30) & (frequencies < 40)])
        band_power['delta_power'] = np.sum(psd[(frequencies >= 0.5) & (frequencies < 4)])
        band_power['theta_power'] = np.sum(psd[(frequencies >= 4) & (frequencies < 8)])
        band_power['alpha_power'] = np.sum(psd[(frequencies >= 8) & (frequencies < 12)])
        band_power['beta_power'] = np.sum(psd[(frequencies >= 12) & (frequencies < 30)])
        band_power['gamma_powder'] = np.sum(psd[(frequencies >= 30) & (frequencies < 40)])

        band_power_list.append(band_power)
        timestamp_info.append({'start_time': start_time, 'end_time': end_time})

    # 合并结果
    results = pd.DataFrame(band_power_list)
    time_info = pd.DataFrame(timestamp_info)
    final_results = pd.concat([time_info, results], axis=1)

    return final_results


def resample_to_constant_rate(df, fs=100):
    """
    将非均匀采样数据重采样到恒定速率
    参数：
        df: 包含时间戳和数据的DataFrame
        fs: 目标采样率 (默认100Hz)
    """
    # 确保时间戳是datetime类型
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])

    # 设置时间索引
    df = df.set_index('time_stamp')

    # 创建等间隔时间索引
    start_time = df.index.min()
    end_time = df.index.max()
    new_index = pd.date_range(start=start_time, end=end_time, freq=f"{1000 // fs}ms")

    # 重采样到恒定速率 (线性插值)
    resampled = df.resample(f"{1000 // fs}ms").mean().interpolate(method='linear')

    # 重置索引
    resampled.reset_index(inplace=True)
    return resampled


def convert_to_eeg_amplitude(data):
    """
    将采集数据转换为有意义的EEG幅度（微伏）
    图一中的数据非常小（~10^-5），需要转换
    """
    # 由于用户数据已经是edf_data格式，我们假设它是经过适当缩放的实际EEG值
    # 但原始数据幅度似乎异常小，所以我们扩大倍数使其在典型EEG范围内（μV）
    # 注意：实际应用中应根据校准数据确定缩放因子
    return data * 1e6  # 转换为微伏


# 主处理流程
def process_eeg_file(file_path):
    # 加载数据 (根据图一格式)
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # 转换时间戳
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])

    # # 转换数据幅度 (根据图一数据特点)
    # df['edf_data'] = convert_to_eeg_amplitude(df['edf_data'])

    # 重采样到恒定100Hz采样率
    resampled_df = resample_to_constant_rate(df, fs=100)

    # 计算PSD和特征
    results = compute_psd_with_timestamps(
        eeg_data=resampled_df['edf_data'].values,
        timestamps=resampled_df['time_stamp'],
        fs=100
    )

    return results


# 使用示例
if __name__ == "__main__":
    # 从图一获取文件路径 (修改为实际路径)
    input_file = str(Path(__file__).parent.parent / "EEG_data" / "gjx" / "")
    output_file = str(Path(__file__).parent.parent / "time_frequent_signal" / "gjx" / "")
    # 处理数据
    for i in range(2, 3):
        file_name = "psg_eeg_gjx_0715.csv"
        cmp_path = input_file + file_name
        processed_data = process_eeg_file(cmp_path)
        # 保存结果
        save_file = f"time_frequent_gjx_0715.csv"
        cmp_output_file = output_file + save_file
        processed_data.to_csv(cmp_output_file, index=False)

        print(f"处理完成! 结果保存至: {cmp_output_file}")
        print(f"共处理了 {len(processed_data)} 个30秒周期")

        # 打印前几个周期的特征
        print("\n特征数据示例:")
        print(processed_data.head())