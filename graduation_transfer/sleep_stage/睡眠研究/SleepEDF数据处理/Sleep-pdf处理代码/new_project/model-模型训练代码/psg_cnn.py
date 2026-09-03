"""
用于使用CNN对睡眠阶段的训练的处理
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np


# 1. 数据预处理
class SleepDataset(Dataset):
    def __init__(self, features, labels):
        self.X = features
        self.y = labels

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


dir_path = "F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"
df = pd.read_csv(dir_path)

# 这里使用用户提供的示例数据格式
features = df.drop('label', axis=1).values
labels = df['label'].values

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

batch_size = 32
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size)


# 2. 定义CNN模型
class SleepCNN(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(SleepCNN, self).__init__()
        self.conv1 = nn.Conv1d(1, 32, kernel_size=(3,), padding=1)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=(3,), padding=1)
        self.pool = nn.MaxPool1d(2)

        # 计算全连接层输入尺寸

        self.fc_input_dim = self._calculate_fc_input(input_dim)
        print(f"self._to_linear:{self.fc_input_dim}, num_classes:{num_classes}")
        self.fc = nn.Sequential(
            nn.Linear(self.fc_input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

    def _calculate_fc_input(self, input_dim):
        # 创建虚拟输入 (batch_size=1, channels=1, length=input_dim)
        dummy_input = torch.randn(1, 1, input_dim)
        with torch.no_grad():
            x = self.pool(nn.ReLU()(self.conv1(dummy_input)))
            x = self.pool(nn.ReLU()(self.conv2(x)))
        return x.view(1, -1).size(1)  # 展平后的特征数


    def forward(self, x):
        x = x.unsqueeze(1)  # 添加通道维度 (batch, 1, features)
        x = self.pool(nn.ReLU()(self.conv1(x)))
        x = self.pool(nn.ReLU()(self.conv2(x)))
        x = x.view(x.size(0), -1)
        return self.fc(x)


# 初始化模型
input_dim = features.shape[1]
num_classes = len(torch.unique(labels))  # 根据实际类别数修改
model = SleepCNN(input_dim, num_classes)

# 3. 训练配置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

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
        optimizer.step()

        running_loss += loss.item()

    # 验证
    model.eval()
    all_predicted = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            all_predicted.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # 计算指标
    accuracy = 100 * (np.array(all_predicted) == np.array(all_labels)).mean()
    precision = precision_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
    recall = recall_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
    f1 = f1_score(all_labels, all_predicted, average='macro', zero_division=0) * 100

    print(
        f"Epoch {epoch + 1}/{num_epochs}, Loss: {running_loss / len(train_loader):.4f}, "
        f"准确率: {accuracy:.2f}%, 精确率: {precision:.2f}%, 召回率: {recall:.2f}%, F1-score: {f1:.2f}%")