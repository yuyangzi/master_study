"""
整合所有的数据的处理流程
"""
import pandas as pd
import numpy as np
from scipy import signal
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from torch.utils.data import Dataset, DataLoader
from pathlib import Path


class SleepLSTM(nn.Module):
    def __init__(self, config):
        super(SleepLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=config["input_size"],
            hidden_size=config["hidden_size"],
            num_layers=config["num_layers"],
            batch_first=True,
            dropout=config["dropout"] if config["num_layers"] > 1 else 0
        )
        self.dropout = nn.Dropout(config["dropout"])
        self.fc = nn.Linear(config["hidden_size"], config["num_classes"])

    def forward(self, x):
        h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = out[:, -1, :]
        out = self.dropout(out)
        out = self.fc(out)
        return out


def pad_sequence_front(features, idx, sequence_length):
    """从0到idx取数据，并向前填充不足的部分"""
    seq = features[0:idx + 1]
    if len(seq) < sequence_length:
        # 使用0进行填充
        pad_length = sequence_length - len(seq)
        seq = np.pad(seq, ((pad_length, 0), (0, 0)), mode='constant', constant_values=0)
    return seq[-sequence_length:]  # 总是返回固定长度的序列


class NewSleepDataset(Dataset):
    def __init__(self, features, sequence_length=10):
        self.features = features.numpy() if isinstance(features, torch.Tensor) else features
        self.sequence_length = sequence_length

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        seq_features = pad_sequence_front(self.features, idx, self.sequence_length)
        return torch.FloatTensor(seq_features)


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
        band_power = {
            'mean': np.mean(segment),
            'std': np.std(segment),
            'max': np.max(segment),
            'min': np.min(segment),
            'energy': np.sum(segment ** 2),
            'delta_power': np.sum(psd[(frequencies >= 0.5) & (frequencies < 4)]),
            'theta_power': np.sum(psd[(frequencies >= 4) & (frequencies < 8)]),
            'alpha_power': np.sum(psd[(frequencies >= 8) & (frequencies < 12)]),
            'beta_power': np.sum(psd[(frequencies >= 12) & (frequencies < 30)]),
            'gamma_powder': np.sum(psd[(frequencies >= 30) & (frequencies < 40)])
        }

        band_power_list.append(band_power)
        timestamp_info.append({'start_time': start_time, 'end_time': end_time})

    # 合并结果
    results = pd.DataFrame(band_power_list)
    time_info = pd.DataFrame(timestamp_info)
    final_results = pd.concat([time_info, results], axis=1)

    return final_results


class CompleteDealDataset(object):
    def __init__(self, user_name="test"):
        if user_name == "test":
            raise ValueError(f"请输入对应的用户名称,且将原始数据放在sleep_stage/EEG_data/complete_path/{user_name}下")
        self.user_name = user_name
        # 最优模型的路径
        self.model_path = str(Path(__file__).parent.parent / "model" / "rnn_lstm" / "best_model_epoch36.pth")
        # 原始数据的路径
        self.raw_path = str(Path(__file__).parent.parent / "EEG_data" / "complete_path" / "") + user_name + "/"
        # PSG的数据的处理
        self.psg_deal_path = str(Path(__file__).parent.parent / "PSG_deal_data" / "deal_data" / "")
        # PSG打上标签的数据
        self.psg_label_path = str(Path(__file__).parent.parent / "PSG_deal_data" / "label_data" / "")
        # 获取EEG时域和频域的信号数据
        self.psg_fr_date_path = str(Path(__file__).parent.parent / "PSG_deal_data" / "frequent_date_data" / "")
        # IMU的数据处理
        self.imu_deal_path = str(Path(__file__).parent.parent / "IMU_deal_data" / "deal_data" / "")
        # IMU打上标签的数据
        self.imu_label_path = str(Path(__file__).parent.parent / "IMU_deal_data" / "label_data" / "")
        # 需要修改的数据
        # eeg的data
        self.eeg_origin_data_file = "eeg_liu.xls"
        # imu的data
        self.imu_origin_data_file = "imu_liu.xls"

    def resample_to_constant_rate(self, df, fs=100):
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

        # 重采样到恒定速率 (线性插值)
        resampled = df.resample(f"{1000 // fs}ms").mean().interpolate(method='linear')

        # 重置索引
        resampled.reset_index(inplace=True)
        return resampled

    def process_eeg_file(self, file_path):
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
        resampled_df = self.resample_to_constant_rate(df, fs=100)

        # 计算PSD和特征
        results = compute_psd_with_timestamps(
            eeg_data=resampled_df['edf_data'].values,
            timestamps=resampled_df['time_stamp'],
            fs=100
        )

        return results

    def psg_mid_data_deal(self):
        """
        用于将对应的的eeg的data进行处理
        :return:
        """
        file_path = self.raw_path + self.eeg_origin_data_file
        save_path = self.psg_deal_path + f"{self.user_name}_mid_eeg.csv"
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
            # 假设 raw_adc 是 numpy array，存储 ADS1220 原始整数值
            # V_REF = 2.048
            # PGA = 1
            # G_AMP = 1000
            # ADC_FULL = 2 ** 23  # 24-bit ADC
            #
            # # 转换为 EEG µV
            # eeg_uv = (raw_val / ADC_FULL) * (V_REF / PGA) / G_AMP * 1e6
            # return eeg_uv
            #
            # eeg_sig = raw_val * 2.048 / float(0x7FFFFF) / 1000
            # return eeg_sig

        # 应用转换函数
        df['edf_data'] = df['clean_signal'].apply(convert_to_edf)

        # 最终保留的列：完整时间戳、原始信号和转换后的EDF数据
        result = df[['time_stamp', 'edf_data']]
        # 检查结果
        print(result.head())
        # 可选：额外格式转换
        result.to_csv(save_path, index=False)
        print("----------------------------------------------------")
        print("psg_mid_data_deal任务执行完成")

    def imu_mid_data_deal(self):
        file_path = self.raw_path + self.imu_origin_data_file
        save_path = self.imu_deal_path + f"{self.user_name}_mid_imu.csv"
        # 根据您的描述：第一列时间戳，第二列信号数据
        file = pd.read_csv(file_path, sep='\t', header=None)
        print(file.head())
        # 给列名
        file.columns = ['time_stamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz']
        # 保存为标准CSV文件
        file.to_csv(save_path, index=False)
        print("----------------------------------------------------")
        print("imu_mid_data_deal任务完成")

    def eeg_data_transfer_to_fr_date_data(self):
        """
        将EEG的信号数据转化为时域和频域的信号
        :return:
        """
        # 输入的数据
        input_file = self.psg_deal_path + f"{self.user_name}_mid_eeg.csv"
        # 输出的数据
        output_file = self.psg_fr_date_path + f"{self.user_name}_eeg_fr_date.csv"

        processed_data = self.process_eeg_file(input_file)
        processed_data.to_csv(output_file, index=False)
        print("----------------------------------------------------")
        print("eeg_data_transfer_to_fr_date_data 任务完成")

    def psg_fr_date_data_add_label(self):
        """
        为fr date的数据打上对应的标签数据
        :return:
        """

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 先加载配置信息
        checkpoint = torch.load(self.model_path, map_location=device)
        config = checkpoint['config']

        # 实例化模型
        model = SleepLSTM(config).to(device)
        # 加载模型参数
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()  # 设置为评估模式

        csv_file_path = self.psg_fr_date_path + f"{self.user_name}_eeg_fr_date.csv"
        csv_save_path = self.psg_label_path + f"{self.user_name}_psg_label.csv"
        df_new = pd.read_csv(csv_file_path)
        # 提取特征列（从 mean 到 gamma_power）
        features_columns = df_new.columns[2:]  # 假设 start_time 和 end_time 是前两列
        features_new = df_new[features_columns].values
        # 使用训练时的 scaler 进行标准化（如果你保存了的话）
        scaler = StandardScaler()
        # 注意：这里只是演示，实际应使用训练集 fit 的 scaler！
        scaled_features_new = scaler.fit_transform(features_new)  # 如果有训练集的 scaler，直接用它 transform
        # 转换为 PyTorch 张量
        scaled_features_tensor = torch.FloatTensor(scaled_features_new)

        # 创建数据集和数据加载器
        sequence_length = config["sequence_length"]
        dataset_new = NewSleepDataset(scaled_features_tensor, sequence_length)
        data_loader_new = DataLoader(dataset_new, batch_size=config["batch_size"], shuffle=False, drop_last=False)

        predictions = []

        with torch.no_grad():
            for inputs in data_loader_new:
                inputs = inputs.to(device)
                outputs = model(inputs)
                _, predicted_classes = torch.max(outputs, 1)
                predictions.extend(predicted_classes.cpu().numpy())
        # 将预测结果添加到原始 DataFrame 中
        df_new['predicted_label'] = predictions  # 前 sequence_length-1 行没有预测值
        # 保存带有预测标签的新 CSV 文件
        df_new.to_csv(csv_save_path, index=False)
        print("----------------------------------------------------")
        print("psg_fr_date_data_add_label任务完成")

    def add_imu_data_label(self):
        """
        给IMU的data增加对应的标签
        :return:
        """
        # 读取文件1（含 start_time, end_time, predicted_label）
        label_path = self.psg_label_path + f"{self.user_name}_psg_label.csv"
        file1 = pd.read_csv(label_path)
        # 确保时间列是数字格式（浮点或整数）
        # 将 start_time 和 end_time 转为 datetime 对象
        file1['start_time'] = pd.to_datetime(file1['start_time'], format='%Y-%m-%d %H:%M:%S.%f')
        file1['end_time'] = pd.to_datetime(file1['end_time'], format='%Y-%m-%d %H:%M:%S.%f')

        # 转为浮点型时间戳（秒数）
        file1['start_ts'] = file1['start_time'].apply(lambda x: x.timestamp())
        file1['end_ts'] = file1['end_time'].apply(lambda x: x.timestamp())
        # 读取文件2（IMU数据），比如：
        # timestamp,x,y,z ...
        imu_path = self.imu_deal_path + f"{self.user_name}_mid_imu.csv"
        file2 = pd.read_csv(imu_path)

        # 确保时间戳是数字格式
        # 格式： '3:48:59.930 2025/3/30' → datetime
        file2[['clock', 'date']] = file2['time_stamp'].str.split(' ', expand=True)
        # 拼接成完整时间字符串：2025/3/30 03:48:59.930
        file2['datetime_str'] = file2['date'] + ' ' + file2['clock']

        # 转换为 datetime 对象
        file2['datetime'] = pd.to_datetime(file2['datetime_str'], format='%Y/%m/%d %H:%M:%S.%f')

        # 转换为浮点时间戳
        file2['timestamp'] = file2['datetime'].apply(lambda x: x.timestamp())
        # 添加 predicted_label 列
        file2['predicted_label'] = None
        # 匹配标签
        for _, row in file1.iterrows():
            mask = (file2['timestamp'] >= row['start_ts']) & (file2['timestamp'] <= row['end_ts'])
            file2.loc[mask, 'predicted_label'] = row['predicted_label']

        output_path = self.imu_label_path + f"{self.user_name}_imu_label.csv"
        # 只保留需要的列
        output = file2[['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'predicted_label']]
        output = output.dropna(subset=['predicted_label'])
        output = output[output['ax'] != 0]
        output = output[output['ay'] != 0]
        output = output[output['az'] != 0]
        output = output[output['gx'] != 0]
        output = output[output['gy'] != 0]
        output = output[output['gz'] != 0]
        output.to_csv(output_path, index=False)
        print("------------------------------------")
        print("add_imu_data_label完成任务")

    def main_process(self):
        # 处理eeg数据
        self.psg_mid_data_deal()
        # 处理IMU的数据
        self.imu_mid_data_deal()
        # 处理psg的时域频域数据
        self.eeg_data_transfer_to_fr_date_data()
        # 给PSG数据打上标签
        self.psg_fr_date_data_add_label()
        # 给IMU的数据打上标签
        self.add_imu_data_label()


if __name__ == '__main__':
    CompleteDealDataset(user_name="liu").main_process()
