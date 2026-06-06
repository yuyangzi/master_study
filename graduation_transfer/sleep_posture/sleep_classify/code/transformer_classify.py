import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
from tqdm import tqdm
import numpy as np
import os


class TransformerClassifier(nn.Module):
    def __init__(self, input_dim, num_classes, num_heads, num_encoder_layers, d_model, d_ff):
        super(TransformerClassifier, self).__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.num_heads = num_heads
        self.num_encoder_layers = num_encoder_layers
        self.d_model = d_model
        self.d_ff = d_ff

        self.encoder_layers = nn.TransformerEncoderLayer(d_model=d_model, nhead=num_heads, dim_feedforward=d_ff)
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layers, num_layers=num_encoder_layers)
        self.classifier = nn.Linear(d_model, num_classes)

    def forward(self, x):
        x = x.unsqueeze(0)  # Add sequence dimension
        x = self.transformer_encoder(x)
        x = x.squeeze(0)  # Remove sequence dimension
        out = self.classifier(x)
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
input_dim = 6  # 鸢尾花数据集的特征数量
num_classes = 3  # 类别数量
num_heads = 2
num_encoder_layers = 3
d_model = 64
d_ff = 256
model = TransformerClassifier(input_dim, num_classes, num_heads, num_encoder_layers, d_model, d_ff)

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