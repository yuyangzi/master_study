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
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16)


# 3. 定义LSTM模型
class SleepLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(SleepLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        out, _ = self.lstm(x, (h0, c0))  # 输出形状：(batch, seq_len, hidden_size)
        out = self.dropout(out[:, -1, :])  # 取最后一个时间步
        out = self.fc(out)
        return out


# 初始化模型
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SleepLSTM(
    input_size=10,
    hidden_size=64,
    num_layers=2,
    num_classes=4
).to(device)

# 4. 训练配置
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', patience=5)

# 5. 训练循环
best_acc = 0.0
for epoch in range(50):
    model.train()
    total_loss = 0.0

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item()

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
    val_acc = 100 * (np.array(all_predicted) == np.array(all_labels)).mean()
    precision = precision_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
    recall = recall_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
    f1 = f1_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
    
    scheduler.step(val_acc)

    # # 保存最佳模型
    # if val_acc > best_acc:
    #     best_acc = val_acc
    #     torch.save(model.state_dict(), 'best_lstm_model.pth')

    # 打印训练信息
    # if (epoch + 1) % 10 == 0:
    print(f'Epoch [{epoch + 1}/50] | Loss: {total_loss / len(train_loader):.4f} | '
          f'准确率: {val_acc:.2f}% | 精确率: {precision:.2f}% | 召回率: {recall:.2f}% | F1-score: {f1:.2f}%')