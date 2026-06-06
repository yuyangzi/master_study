import mne
import numpy as np
import pandas as pd
import os
import random
from scipy.signal import welch
from datetime import datetime
from pathlib import Path


class NewEDFDataDeal(object):

    def __init__(self, sample_count=10):
        # 数据集所在的文件夹
        self.dir_path = str(Path(__file__).parent.parent.parent.parent / "all_data" / "sleep-cassette" / "")
        # 每次训练需要获取的样本个数
        self.sample_count = sample_count
        # 用于保存的数据位置
        date_str = datetime.now().strftime("%Y_%m_%d_%H")
        self.save_path = str(Path(__file__).parent.parent / "merge_data" / "") + date_str + "_data.csv"

    def deal_all_data(self):
        # 返回的列表中为feature_file:label_file
        file_list = list()
        for root, dirs, file_names in os.walk(self.dir_path):
            for file_name in file_names:
                file_list.append(file_name)
        # 进行排序
        sort_file_names = sorted(file_list)
        integrate_file_list = list()
        for i in range(len(sort_file_names)):
            if i % 2 == 1:
                # 表示为奇数时用于进行数据分类处理
                feature_file = sort_file_names[i - 1]
                label_file = sort_file_names[i]
                integrate_file = feature_file + ":" + label_file
                integrate_file_list.append(integrate_file)
        print(f"length of integrate_file_list:{len(integrate_file_list)}")
        # 随机获取10条对应的数据进行返回
        ret_list = random.sample(integrate_file_list, self.sample_count)
        return ret_list

    def extract_features(self, segment, sampling_rate):
        # 时域特征
        mean_val = np.mean(segment) # 平均值
        std_val = np.std(segment)   # 標準差
        max_val = np.max(segment)   # 最大值
        min_val = np.min(segment)   # 最小值
        energy_val = np.sum(segment ** 2)  # 平方和

        # 频域特征
        freqs, psd = welch(segment, fs=sampling_rate)
        delta_power = np.sum(psd[(freqs >= 0.5) & (freqs < 4)])  # Delta 波
        theta_power = np.sum(psd[(freqs >= 4) & (freqs < 8)])  # Theta 波
        alpha_power = np.sum(psd[(freqs >= 8) & (freqs < 12)])  # Alpha 波
        beta_power = np.sum(psd[(freqs >= 12) & (freqs < 30)])  # Beta 波
        gamma_powder = np.sum(psd[(freqs >= 30) & (freqs < 40)])  # gamma波

        return [mean_val, std_val, max_val, min_val, energy_val,
                delta_power, theta_power, alpha_power, beta_power, gamma_powder]

    def normal_feature_dataset(self):
        """
        用于标准化对应的数据集
        :return:
        """
        integrate_file_list = self.deal_all_data()
        # 对应的edf数据文件
        psg_files = list()
        # 对应的edf的标签文件
        annot_files = list()
        for integrate_file in integrate_file_list:
            file_list = integrate_file.split(":")
            # 特征数据完整路径列表
            psg_file = self.dir_path + file_list[0]
            psg_files.append(psg_file)
            # 标签数据完整路径列表
            annot_file = self.dir_path + file_list[1]
            annot_files.append(annot_file)

        aligned_data = []
        # 初始化列表保存数据和标签
        features = []
        labels = []
        # 开始对应的处理数据
        stage_set = set()
        for psg_file, hypnogram_file in zip(psg_files, annot_files):
            # print("--------------------------------")
            # print(f"psg_file:{psg_file}")
            # print(f"hypnogram_file:{hypnogram_file}")
            # print("--------------------------------")
            # 首先读取对应原始数据集
            raw_psg = mne.io.read_raw_edf(psg_file, preload=True)
            # 获取采样率和通道数据
            sampling_rate = raw_psg.info['sfreq']  # 采样率（单位：Hz）
            # 提取 EEG Fpz-Cz 通道数据
            print(f"raw_psg.ch_names:{raw_psg.ch_names}")
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

            for i, (stage, onset, duration) in enumerate(zip(sleep_stages, onsets, durations)):
                start_sample = int(round(onset) * sampling_rate)  # 起始样本点
                end_sample = int(round(onset + duration) * sampling_rate)  # 结束样本点
                eeg_segment = eeg_data[start_sample:end_sample]  # 对应时间段的 EEG 数据
                aligned_data.append({
                    "stage": stage,
                    "data": eeg_segment,
                    "start_time": onset,
                    "end_time": onset + duration,
                    "duration": duration,
                    "sampling_rate": sampling_rate
                })
        stage_mapping = {
            'Sleep stage W': 0, 'Sleep stage 1': 1, 'Sleep stage 2': 1,
            'Sleep stage 3': 2, 'Sleep stage 4': 2, 'Sleep stage R': 3
        }
        # 合并所有的数据为测试数据
        # 遍历每个睡眠阶段的数据段
        for segment in aligned_data:
            eeg_segment = segment['data']  # EEG 数据
            stage = segment['stage']  # 睡眠阶段（标签）
            sampling_rate = segment["sampling_rate"]
            window_length = int(30 * sampling_rate)  # 30秒窗口
            label = stage_mapping.get(stage, -1)
            if label == -1:
                continue  # 跳过无效标签
            for i in range(0, len(eeg_segment), window_length):
                window = eeg_segment[i:i + window_length]
                if len(window) == window_length:
                    feature_vector = self.extract_features(window, sampling_rate)
                    print(f"feature_vector:{feature_vector}, label:{label}")
                    features.append(feature_vector)
                    labels.append(label)


        columns = ['mean', 'std', 'max', 'min', 'energy',
                   'delta_power', 'theta_power', 'alpha_power', 'beta_power', 'gamma_powder']
        df = pd.DataFrame(features, columns=columns)
        df['label'] = labels
        # 打印数据集
        print(df.head())
        print("-------开始保存数据--------")
        df.to_csv(self.save_path, index=False)

# 使用30s作为一个窗口提取对应的时域和频域的信号，将睡眠阶段3， 4合并为3阶段， 作为5个阶段


if __name__ == "__main__":
    NewEDFDataDeal(sample_count=60).normal_feature_dataset()
