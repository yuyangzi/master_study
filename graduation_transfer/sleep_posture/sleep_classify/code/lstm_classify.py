import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
from tqdm import tqdm
import numpy as np
import os


class LSTMClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(LSTMClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        h0 = torch.zeros(1, x.size(0), self.hidden_dim).requires_grad_()
        c0 = torch.zeros(1, x.size(0), self.hidden_dim).requires_grad_()
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])  # 取最后一个时间步的输出
        return out

# 1. 加载相关的数据
path = "../after_process_data/after_process_data/"
# 获取所有的不是motion得excel的文件
execl_files = [f for f in os.listdir(path) if not f.endswith("motion.xlsx")]
# 创建一个进度条
progress_bar = tqdm(total=len(execl_files), desc="progress file")
column_names = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'feature6', "label"]
# 创建一个空的DataFrame的数据
dataframes = list()
# 2 数据处理
for file_name in execl_files:
    file_path = os.path.join(path, file_name)
    df = pd.read_excel(file_path, header=None)
    if file_name.endswith("left.xlsx"):
        # 表示左躺睡觉
        df["label"] = 0
    elif file_name.endswith("m.xlsx"):
        # 表示正常睡觉
        df["label"] = 1
    else:
        # 表示右躺睡觉
        df["label"] = 2
    # 当前的文件追加到all_data中
    dataframes.append(df)
    progress_bar.update(1)
progress_bar.close()  # 完成时关闭进度条
new_df = pd.concat(dataframes, ignore_index=False)
new_df.label = new_df.label.astype(np.int32)
# 3. 根据需求获取最原始的特征属性矩阵X和目标属性Y
X = new_df.iloc[:, :-1]
# print(X.shape)
Y = new_df.iloc[:, -1]

# 将数据集分为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 将数据转换为PyTorch张量
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.long)

# 实例化模型
input_size = 6  # 鸢尾花数据集的特征数量
hidden_size = 10  # 隐藏层的大小
output_size = 3  # 输出层的大小（鸢尾花数据集的类别数）
model = LSTMClassifier(input_size, hidden_size, output_size)

# 3. 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 4
# 训练模型
epochs = 100
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    output = model(X_train)
    loss = criterion(output, y_train)
    loss.backward()
    optimizer.step()

    if (epoch+1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

# 评估模型
model.eval()
with torch.no_grad():
    predictions = model(X_test)
    predicted_classes = torch.argmax(predictions, dim=1)
    accuracy = (predicted_classes == y_test).float().mean().item()
    print(f'Test Accuracy: {accuracy:.2f}')