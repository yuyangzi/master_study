"""
用于使用CNN+LSTM混合模型对睡眠阶段的训练处理
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
from pathlib import Path


# 1. 数据预处理
class SleepDataset(Dataset):
    def __init__(self, features, labels):
        self.X = features
        self.y = labels

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


dir_path = str(Path(__file__).parent.parent / "base_data" / "train_label.csv")
df = pd.read_csv(dir_path)

# 这里使用用户提供的示例数据格式
features = df.drop('predicted_label', axis=1).values
labels = df['predicted_label'].values

# 数据标准化
scaler = StandardScaler()
features = scaler.fit_transform(features)

# 转换为Tensor
features = torch.FloatTensor(features)
labels = torch.LongTensor(labels)  # 假设标签是整数形式

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42
)

# 创建DataLoader
train_dataset = SleepDataset(X_train, y_train)
test_dataset = SleepDataset(X_test, y_test)

batch_size = 2048
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size)


# 2. 定义CNN+LSTM混合模型
class SleepCNNLSTM(nn.Module):
    def __init__(self, input_dim, num_classes, lstm_hidden_size=64, lstm_num_layers=2):
        super(SleepCNNLSTM, self).__init__()
        
        # CNN部分：提取局部特征
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool1d(2)
        self.relu = nn.ReLU()
        
        # 计算CNN输出后的特征维度
        # 经过两次pooling后，长度变为 input_dim // 4
        cnn_output_length = input_dim // 4
        cnn_output_channels = 64
        
        # LSTM部分：处理时序特征
        # 将CNN的输出特征图的空间维度作为序列长度，通道数作为特征维度
        self.lstm = nn.LSTM(
            input_size=cnn_output_channels,
            hidden_size=lstm_hidden_size,
            num_layers=lstm_num_layers,
            batch_first=True,
            dropout=0.2 if lstm_num_layers > 1 else 0
        )
        
        # 全连接层
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Sequential(
            nn.Linear(lstm_hidden_size, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )
        
        self.lstm_hidden_size = lstm_hidden_size
        self.lstm_num_layers = lstm_num_layers
    
    def forward(self, x):
        # x shape: (batch_size, input_dim)
        # CNN部分
        x = x.unsqueeze(1)  # 添加通道维度 (batch_size, 1, input_dim)
        x = self.pool(self.relu(self.conv1(x)))  # (batch_size, 32, input_dim//2)
        x = self.pool(self.relu(self.conv2(x)))  # (batch_size, 64, input_dim//4)
        
        # 转换为LSTM输入格式: (batch_size, seq_len, input_size)
        # 将空间维度作为序列长度，通道维度作为特征维度
        x = x.permute(0, 2, 1)  # (batch_size, input_dim//4, 64)
        
        # LSTM部分
        # 初始化LSTM的隐藏状态
        h0 = torch.zeros(self.lstm_num_layers, x.size(0), self.lstm_hidden_size).to(x.device)
        c0 = torch.zeros(self.lstm_num_layers, x.size(0), self.lstm_hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))  # out: (batch_size, seq_len, hidden_size)
        out = out[:, -1, :]  # 取最后一个时间步的输出 (batch_size, hidden_size)
        
        # 全连接层
        out = self.dropout(out)
        out = self.fc(out)
        return out


# 初始化模型
input_dim = features.shape[1]
num_classes = len(torch.unique(labels))
model = SleepCNNLSTM(input_dim, num_classes, lstm_hidden_size=64, lstm_num_layers=2)

# 3. 训练配置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', patience=5)

# 4. 训练循环
num_epochs = 50

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        running_loss += loss.item()

    # 验证
    model.eval()
    correct = 0
    total = 0
    all_predicted = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            # 收集所有预测和真实标签用于计算指标
            all_predicted.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # 计算指标（转换为百分比）
    accuracy = 100 * correct / total
    precision = 100 * precision_score(all_labels, all_predicted, average='weighted', zero_division=0)
    recall = 100 * recall_score(all_labels, all_predicted, average='weighted', zero_division=0)
    f1 = 100 * f1_score(all_labels, all_predicted, average='weighted', zero_division=0)
    scheduler.step(accuracy)

    print(
        f"Epoch {epoch + 1}/{num_epochs}, Loss: {running_loss / len(train_loader):.4f}, "
        f"Accuracy: {accuracy:.2f}%, Precision: {precision:.2f}%, Recall: {recall:.2f}%, F1-Score: {f1:.2f}%")

