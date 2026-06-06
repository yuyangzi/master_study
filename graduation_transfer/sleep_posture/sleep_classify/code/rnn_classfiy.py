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


class RNNClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(RNNClassifier, self).__init__()
        self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # 初始化隐藏状态
        h0 = torch.zeros(1, x.size(0), 10).to(x.device)

        # 前向传播
        out, _ = self.rnn(x, h0)
        # 取最后一个时间步的输出
        out = self.fc(out[:, -1, :])
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
input_size = 4  # 鸢尾花数据集的特征数量
hidden_size = 10  # 隐藏层的大小
output_size = 3  # 输出层的大小（鸢尾花数据集的类别数）
model = RNNClassifier(input_size, hidden_size, output_size)

# 3. 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 4. 训练模型
num_epochs = 10
for epoch in range(num_epochs):
    model.train()

    # 将数据重塑为适合RNN的格式 [batch_size, seq_length, input_size]
    X_train_rnn = X_train_tensor.view(-1, 1, input_size)

    # 清除之前的梯度
    optimizer.zero_grad()

    # 前向传播
    outputs = model(X_train_rnn)
    loss = criterion(outputs, y_train_tensor)

    # 反向传播和优化
    loss.backward()
    optimizer.step()

# 5. 评估模型
model.eval()
with torch.no_grad():
    y_pred = model(X_test_tensor.view(-1, 1, input_size))
    _, predicted = torch.max(y_pred.data, 1)
    correct = (predicted == y_test_tensor).sum().item()
    accuracy = correct / y_test_tensor.size(0)
    print(f'Test Accuracy: {accuracy * 100:.2f}%')