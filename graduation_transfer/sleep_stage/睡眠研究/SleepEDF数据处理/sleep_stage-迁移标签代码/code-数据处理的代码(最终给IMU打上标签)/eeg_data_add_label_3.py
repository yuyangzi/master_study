"""
将对应的睡眠数据增加对应的
"""
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from torch.utils.data import Dataset, DataLoader
import numpy as np
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
    seq = features[0:idx+1]
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


# 设备配置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载模型和配置
checkpoint_path = "../model/rnn_lstm/best_model_epoch32.pth"  # 替换为你实际的路径
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 先加载配置信息
checkpoint = torch.load(checkpoint_path, map_location=device)

config = checkpoint['config']

# 实例化模型
model = SleepLSTM(config).to(device)

# 加载模型参数
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()  # 设置为评估模式


csv_file_path = str(Path(__file__).parent.parent / "time_frequent_signal" / "gjx" / "")
csv_save_path = str(Path(__file__).parent.parent / "time_frequent_signal" / "label_gjx" / "")

for i in range(2, 3):
    file_path = csv_file_path + "time_frequent_gjx_0715.csv"
    save_path = csv_save_path + "time_frequent_label_gjx_0715.csv"
    df_new = pd.read_csv(file_path)
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
    df_new.to_csv(save_path, index=False)
    print(f"完成:{i}:{save_path}")

