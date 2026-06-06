"""
用于生成混淆矩阵，用于SCI论文中的图
基于psg_rnn_lstm.py的逻辑和数据
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 设置中文字体和样式（用于SCI论文）
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']  # 使用Arial字体（SCI论文常用）
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("deep")

# 设备配置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 超参数配置（与psg_rnn_lstm.py保持一致）
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


# 数据预处理类（与psg_rnn_lstm.py保持一致）
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


# 定义RNN+LSTM模型（与psg_rnn_lstm.py保持一致）
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


# 数据加载（与psg_rnn_lstm.py保持一致）
dir_path = "F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"
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

# 初始化模型
model = SleepLSTM().to(device)

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=config["learning_rate"])

# 训练模型
print("开始训练模型...")
for epoch in range(config["num_epochs"]):
    model.train()
    total_loss = 0
    for inputs, labels in train_loader:
        inputs = inputs.to(device)
        labels = labels.squeeze().to(device)

        outputs = model(inputs)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    # 验证
    model.eval()
    all_predicted = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            labels = labels.squeeze().to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            all_predicted.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # 计算指标
    accuracy = 100 * (np.array(all_predicted) == np.array(all_labels)).mean()
    precision = precision_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
    recall = recall_score(all_labels, all_predicted, average='macro', zero_division=0) * 100
    f1 = f1_score(all_labels, all_predicted, average='macro', zero_division=0) * 100

    if (epoch + 1) % 10 == 0:
        print(
            f"Epoch [{epoch + 1}/{config['num_epochs']}],"
            f" Loss: {total_loss / len(train_loader):.4f}, "
            f"准确率: {accuracy:.2f}%, 精确率: {precision:.2f}%, 召回率: {recall:.2f}%, F1-score: {f1:.2f}%")

print("训练完成！")

# 在完整测试集上生成预测用于混淆矩阵
model.eval()
all_predicted = []
all_labels = []
with torch.no_grad():
    for inputs, labels in test_loader:
        inputs = inputs.to(device)
        labels = labels.squeeze().to(device)
        outputs = model(inputs)
        _, predicted = torch.max(outputs.data, 1)
        all_predicted.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# 计算混淆矩阵
cm = confusion_matrix(all_labels, all_predicted)

# 计算百分比混淆矩阵（用于显示）
cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

# 自动检测类别数量和标签
unique_labels = sorted(np.unique(all_labels))
num_classes = len(unique_labels)

# 类别标签（根据实际类别调整，常见的睡眠阶段标签）
# 如果标签是0,1,2,3，则对应Wake, Stage 1, Stage 2, REM
if num_classes == 4:
    class_names = ['Wake', 'Stage 1', 'Stage 2', 'REM']
elif num_classes == 5:
    class_names = ['Wake', 'Stage 1', 'Stage 2', 'Stage 3', 'REM']
else:
    # 如果类别数不是4或5，使用通用标签
    class_names = [f'Class {i}' for i in unique_labels]

print(f"检测到 {num_classes} 个类别，标签: {unique_labels}")
print(f"类别名称: {class_names}")

# 创建混淆矩阵图（适合SCI论文）
fig, ax = plt.subplots(figsize=(8, 6))

# 使用seaborn绘制热力图，添加数值和百分比
annot = np.empty_like(cm).astype(str)
n_rows, n_cols = cm.shape
for i in range(n_rows):
    for j in range(n_cols):
        c = cm[i, j]
        p = cm_percent[i, j]
        if c == 0:
            annot[i, j] = ''
        else:
            annot[i, j] = f'{c}\n({p:.1f}%)'

sns.heatmap(
    cm,
    annot=annot,
    fmt='',
    cmap='Blues',
    xticklabels=class_names,
    yticklabels=class_names,
    cbar_kws={'label': 'Count'},
    ax=ax,
    linewidths=0.5,
    linecolor='gray',
    annot_kws={'fontsize': 11, 'fontweight': 'bold', 'color': 'black'}
)

# 设置标题和标签
ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold', pad=20)

# 调整布局
plt.tight_layout()

# 保存为高分辨率图片（适合SCI论文）
output_dir = "./figures"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 保存为PNG（高分辨率）
plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), 
            dpi=300, bbox_inches='tight', facecolor='white')
print(f"混淆矩阵已保存到: {os.path.join(output_dir, 'confusion_matrix.png')}")

# 保存为PDF（矢量图，适合论文）
plt.savefig(os.path.join(output_dir, 'confusion_matrix.pdf'), 
            bbox_inches='tight', facecolor='white')
print(f"混淆矩阵已保存到: {os.path.join(output_dir, 'confusion_matrix_new.pdf')}")

# 创建百分比混淆矩阵图（可选，用于更直观的展示）
fig2, ax2 = plt.subplots(figsize=(8, 6))

sns.heatmap(
    cm_percent,
    annot=True,
    fmt='.1f',
    cmap='Blues',
    xticklabels=class_names,
    yticklabels=class_names,
    cbar_kws={'label': 'Percentage (%)'},
    ax=ax2,
    linewidths=0.5,
    linecolor='gray',
    annot_kws={'fontsize': 11, 'fontweight': 'bold', 'color': 'black'}
)

ax2.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
ax2.set_ylabel('True Label', fontsize=12, fontweight='bold')
ax2.set_title('Confusion Matrix (Percentage)', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()

# 保存百分比混淆矩阵
plt.savefig(os.path.join(output_dir, 'confusion_matrix_percent.png'), 
            dpi=300, bbox_inches='tight', facecolor='white')
print(f"百分比混淆矩阵已保存到: {os.path.join(output_dir, 'confusion_matrix_percent.png')}")

plt.savefig(os.path.join(output_dir, 'confusion_matrix_percent.pdf'), 
            bbox_inches='tight', facecolor='white')
print(f"百分比混淆矩阵已保存到: {os.path.join(output_dir, 'confusion_matrix_percent.pdf')}")

# 打印最终评估指标
print("\n最终评估指标:")
print(f"准确率: {100 * (np.array(all_predicted) == np.array(all_labels)).mean():.2f}%")
print(f"精确率: {precision_score(all_labels, all_predicted, average='macro', zero_division=0) * 100:.2f}%")
print(f"召回率: {recall_score(all_labels, all_predicted, average='macro', zero_division=0) * 100:.2f}%")
print(f"F1-score: {f1_score(all_labels, all_predicted, average='macro', zero_division=0) * 100:.2f}%")

plt.show()

