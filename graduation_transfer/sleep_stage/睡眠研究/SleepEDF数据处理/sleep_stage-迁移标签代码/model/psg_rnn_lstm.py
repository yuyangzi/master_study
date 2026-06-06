"""
使用RNN和LSTM进行训练
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from pathlib import Path

# 设备配置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 超参数配置
config = {
    "sequence_length": 10,  # 每个样本的时间步数（根据实际数据调整）
    "input_size": 10,  # 每个时间步的特征数（mean到gamma_power共11个）
    "hidden_size": 64,  # LSTM隐藏层维度
    "num_layers": 2,  # LSTM堆叠层数
    "num_classes": 4,  # 睡眠阶段类别数
    "batch_size": 32,
    "dropout": 0.3,
    "learning_rate": 0.001,
    "num_epochs": 50
}


# 数据预处理类
class SleepDataset(Dataset):
    def __init__(self, features, labels, sequence_length=10):
        self.features = features
        self.labels = labels
        self.sequence_length = sequence_length

    def __len__(self):
        return len(self.features) - self.sequence_length + 1

    def __getitem__(self, idx):
        # 构造时间序列数据
        seq_features = self.features[idx:idx + self.sequence_length]
        label = self.labels[idx + self.sequence_length - 1]  # 取最后一个时间步的标签
        return torch.FloatTensor(seq_features), torch.LongTensor([label])

# 数据加载
dir_path = str(Path(__file__).parent.parent.parent / "Sleep-pdf处理代码" / "new_project" / "merge_data" / "balanced_sort_2025_09_15_21_data.csv")
df = pd.read_csv(dir_path)
features = df.drop('label', axis=1).values
labels = df['label'].values

# 标准化特征
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# 转换为PyTorch张量
scaled_features = torch.FloatTensor(scaled_features)
labels = torch.LongTensor(labels)

# 创建数据集
dataset = SleepDataset(scaled_features, labels, config["sequence_length"])

# 划分训练测试集
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

train_loader = DataLoader(train_dataset, batch_size=config["batch_size"], shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=config["batch_size"])


# 定义RNN+LSTM模型
class SleepLSTM(nn.Module):
    def __init__(self):
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
        # x shape: (batch_size, seq_length, input_size)
        h0 = torch.zeros(config["num_layers"], x.size(0), config["hidden_size"]).to(device)
        c0 = torch.zeros(config["num_layers"], x.size(0), config["hidden_size"]).to(device)

        out, _ = self.lstm(x, (h0, c0))  # out: (batch_size, seq_length, hidden_size)
        out = out[:, -1, :]  # 取最后一个时间步的输出
        out = self.dropout(out)
        out = self.fc(out)
        return out


model = SleepLSTM().to(device)
# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=config["learning_rate"])

best_val_acc = 0.0
checkpoint_dir = "./rnn_lstm"
# 训练循环
for epoch in range(config["num_epochs"]):
    model.train()
    total_loss = 0
    for inputs, labels in train_loader:
        inputs = inputs.to(device)
        labels = labels.squeeze().to(device)  # 调整标签形状

        outputs = model(inputs)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    # 验证
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            labels = labels.squeeze().to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    val_acc = 100 * correct / total
    print(f"Epoch {epoch + 1:03d} | Loss: {total_loss / len(train_loader):.4f} | Val Acc: {val_acc:.2f}%")

    # 保存最佳模型
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        checkpoint = {
            'epoch': epoch+1,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'best_val_acc': best_val_acc,
            'config': config
        }
        # 保存完整模型（包含结构和参数）
        torch.save(checkpoint, f"{checkpoint_dir}/best_model_epoch{epoch+1}.pth")
        print(f"New best model saved with val acc {val_acc:.2f}%")


