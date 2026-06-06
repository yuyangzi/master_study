import mne
import numpy as np
import pandas as pd
from scipy.signal import welch
from pathlib import Path


def test():

    dir_path = str(Path(__file__).parent.parent.parent.parent / "all_data" / "sleep-cassette" / "SC4001E0-PSG.edf")

    raw = mne.io.read_raw_edf(dir_path, preload=True)
    # 2. 查看通道信息
    print("Available channels:", raw.ch_names)
    # 3. 提取 Fpz-Cz 通道
    if "EEG Fpz-Cz" in raw.ch_names:
        EEG_fpz_cz_data = raw.copy().pick_channels(["EEG Fpz-Cz"]).get_data()[0]  # 提取通道数据
        sampling_rate = raw.info['sfreq']  # 采样率
        print(f"Extracted {len(EEG_fpz_cz_data)} data points from Fpz-Cz channel.")
        print(f"fpz_cz_data:{EEG_fpz_cz_data}")
        print(f"Sampling rate: {sampling_rate} Hz")
    else:
        print("Fpz-Cz channel not found in the EDF file.")


def test_Hypnogram():
    dir_path = str(Path(__file__).parent.parent.parent.parent / "all_data" / "sleep-cassette" / "SC4001EC-Hypnogram.edf")
    Annotations = mne.read_annotations(dir_path)

    print("-----Annotations-------")
    print(f"annotation:{Annotations}")

    # 3. 提取睡眠阶段信息
    sleep_stages = Annotations.description  # 睡眠阶段名称，如 "Stage 1", "Stage 2", "REM"
    print(f"sleep_stages:{sleep_stages}")
    print(f"sleep stage :{len(sleep_stages)}")
    onsets = Annotations.onset  # 每个阶段的开始时间（单位：秒）
    print(f"onsets:{onsets}")
    print(f"onsets :{len(onsets)}")
    durations = Annotations.duration  # 每个阶段的持续时间（单位：秒）
    print(f"durations:{durations}")
    print(f"durations :{len(durations)}")


def extract_features(segment, sampling_rate):
    # 时域特征
    mean_val = np.mean(segment)
    std_val = np.std(segment)
    max_val = np.max(segment)
    min_val = np.min(segment)
    energy_val = np.sum(segment ** 2)

    # 频域特征
    freqs, psd = welch(segment, fs=sampling_rate)
    delta_power = np.sum(psd[(freqs >= 0.5) & (freqs < 4)])  # Delta 波
    theta_power = np.sum(psd[(freqs >= 4) & (freqs < 8)])  # Theta 波
    alpha_power = np.sum(psd[(freqs >= 8) & (freqs < 12)])  # Alpha 波
    beta_power = np.sum(psd[(freqs >= 12) & (freqs < 30)])  # Beta 波

    return [mean_val, std_val, max_val, min_val, energy_val,
            delta_power, theta_power, alpha_power, beta_power]


def entire_psg_hypnogram_edf():
    """
    用于处理对应的PSG数据和对应hypnogram注释
    :return:
    """
    # 原始的数据集
    psg_file = str(Path(__file__).parent.parent.parent.parent / "all_data" / "sleep-cassette" / "SC4001E0-PSG.edf")
    # 注释的数据集
    hypnogram_file = str(Path(__file__).parent.parent.parent.parent / "all_data" / "sleep-cassette" / "SC4001EC-Hypnogram.edf")

    # 初始化列表保存数据和标签
    features = []
    labels = []

    # 首先读取对应原始数据集
    raw_psg = mne.io.read_raw_edf(psg_file, preload=True)
    # 获取对应的采样评率

    # 获取采样率和通道数据
    sampling_rate = raw_psg.info['sfreq']  # 采样率（单位：Hz）
    print(f"Sampling rate: {sampling_rate} Hz")

    # 提取 EEG Fpz-Cz 通道数据
    if "EEG Fpz-Cz" in raw_psg.ch_names:
        eeg_data = raw_psg.copy().pick_channels(["EEG Fpz-Cz"]).get_data()[0]  # (samples,)
        print(f"EEG Fpz-Cz data length: {len(eeg_data)} samples")
    else:
        raise ValueError("Channel 'EEG Fpz-Cz' not found in PSG.edf")

    # 2. 加载 Hypnogram 文件中的睡眠阶段
    annotations = mne.read_annotations(hypnogram_file)
    # 提取睡眠阶段的时间信息
    sleep_stages = annotations.description  # 睡眠阶段，如 "Stage 1", "Stage 2", "REM"
    onsets = annotations.onset  # 每个阶段的开始时间（秒）
    durations = annotations.duration  # 每个阶段的持续时间（秒）
    print(f"Number of sleep stages: {len(sleep_stages)}")
    print(f"onsets:{onsets}, length onset:{len(onsets)}")
    print(f"durations:{durations}, length duration:{len(durations)}")

    # # 3. 将 EEG 数据按睡眠阶段分段
    # aligned_data = []
    # for i, (stage, onset, duration) in enumerate(zip(sleep_stages, onsets, durations)):
    #     print(f"index:{i}")
    #     start_sample = int(onset * sampling_rate)  # 起始样本点
    #     end_sample = int((onset + duration) * sampling_rate)  # 结束样本点
    #     eeg_segment = eeg_data[start_sample:end_sample]  # 对应时间段的 EEG 数据
    #
    #     aligned_data.append({
    #         "stage": stage,
    #         "data": eeg_segment,
    #         "start_time": onset,
    #         "end_time": onset + duration,
    #         "duration": duration,
    #         "sampling_rate":sampling_rate
    #     })
    #
    #     print(f"Segment {i + 1}: {stage}, Start: {onset}s, Duration: {duration}s, Data Points: {len(eeg_segment)}")
    # # 将上述的数据进行数据的处理
    # # 遍历每个睡眠阶段的数据段
    # for segment in aligned_data:
    #     eeg_segment = segment['data']  # EEG 数据
    #     stage = segment['stage']  # 睡眠阶段（标签）
    #
    #     # 检查数据长度是否足够
    #     if len(eeg_segment) < 1 * sampling_rate:  # 至少 1 秒的数据
    #         continue
    #
    #     # 提取特征
    #     feature_vector = extract_features(eeg_segment, sampling_rate)
    #     features.append(feature_vector)
    #     labels.append(stage)
    #
    # # 构建 DataFrame
    # columns = ['mean', 'std', 'max', 'min', 'energy',
    #            'delta_power', 'theta_power', 'alpha_power', 'beta_power']
    # df = pd.DataFrame(features, columns=columns)
    # df['label'] = labels
    # # 打印数据集
    # print(df.head())
    # df.to_csv("sleep_stage_dataset.csv", index=False)



if __name__ == "__main__":
    entire_psg_hypnogram_edf()