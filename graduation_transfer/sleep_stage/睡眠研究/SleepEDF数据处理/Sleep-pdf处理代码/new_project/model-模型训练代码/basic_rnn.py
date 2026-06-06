import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import precision_score, recall_score, f1_score
import pandas as pd
import numpy as np

dir_path = "F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"
df = pd.read_csv(dir_path)
# value_to_remove = ['Movement time', 'Sleep stage ?']
# df = df[~df['label'].isin(value_to_remove)]
#
# le = LabelEncoder()
# df['label'] = le.fit_transform(df['label'])
scaler = StandardScaler()
# 获取对应的数据集
X = scaler.fit_transform(df.drop('label', axis=1))
y = df['label']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 将Pandas Series转换为NumPy数组
y_train = y_train.values  # 或者 y_train.to_numpy()
y_test = y_test.values     # 或者 y_test.to_numpy()

# 转换为PyTorch张量并调整形状 [batch_size, seq_len=1, input_size=10]
X_train_tensor = torch.FloatTensor(X_train).unsqueeze(1)
y_train_tensor = torch.LongTensor(y_train)
X_test_tensor = torch.FloatTensor(X_test).unsqueeze(1)
y_test_tensor = torch.LongTensor(y_test)

# 创建数据加载器
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32)


# 3. 定义RNN模型
class SleepRNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(SleepRNN, self).__init__()
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out, _ = self.rnn(x)  # 输出形状：(batch, seq_len, hidden_size)
        out = self.fc(out[:, -1, :])  # 取最后一个时间步
        return out


# 初始化模型
model = SleepRNN(input_size=10, hidden_size=64, num_layers=2, num_classes=4)

# 4. 训练配置
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 5. 训练循环
num_epochs = 100
for epoch in range(num_epochs):
    for inputs, labels in train_loader:
        outputs = model(inputs)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # # 每10个epoch验证一次
    # if (epoch + 1) % 10 == 0:
    with torch.no_grad():
        all_predicted = []
        all_labels = []
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            all_predicted.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
        
        # 计算指标
        accuracy = 100 * (np.array(all_predicted) == np.array(all_labels)).mean()
        precision = precision_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
        recall = recall_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
        f1 = f1_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
        
    print(f'Epoch [{epoch + 1}/{num_epochs}], 准确率: {accuracy:.2f}%, 精确率: {precision:.2f}%, 召回率: {recall:.2f}%, F1-score: {f1:.2f}%')