"""
全连接神经网络进行数据分类
"""
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from torch import Tensor, optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from tqdm import tqdm
import os


# 训练参数的设置
def build_opt(net):
    params = [
        {'params': [], 'lr': 0.001, 'weight_decay': 0.001},  # 保存的是weight参数
        {'params': []}  # 保存的是bias参数
    ]
    for name, param in net.named_parameters():
        if name.endswith(".weight"):
            # 参数就是全连接中的w
            params[0]['params'].append(param)
        else:
            # 当前参数就是全连接中的b
            params[1]['params'].append(param)
    opt = optim.Adam(
        params=params,
        lr=0.001,
        betas=(0.9, 0.999),
        weight_decay=0,
        amsgrad=False
    )
    return opt


class SleepPositionClassify(nn.Module):

    def __init__(self, num_classes=3):
        super(SleepPositionClassify, self).__init__()
        self.classify = nn.Sequential(
            nn.Linear(6, 30),
            nn.ReLU(),
            nn.Linear(30, 30),
            nn.ReLU(),
            nn.Linear(30, num_classes)
        )

    def forward(self, x):
        """
        前向过程
        :param x: [batch_size, 4] batch_size个样本，每个样本4个特征值
        :return: [batch_size, num_classes] batch_size个样本，每个样本属于各个类别的置信度
        """
        z = self.classify(x)
        return z


class NumpyDataset(Dataset):

    def __init__(self, x, y):
        super(NumpyDataset, self).__init__()
        self.x = np.asarray(x, dtype=np.float32)
        self.y = np.asarray(y, dtype=np.int64)


    def __getitem__(self, index: int) -> (Tensor, Tensor):
        _x = self.x[index]  # [e1,]  一个一维的特征向量
        _y = self.y[index] # 一个类别数字标量

        return torch.from_numpy(_x), torch.tensor(_y, dtype=torch.long)

    def __len__(self):
        return len(self.x)


def load_data(batch_size):
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

    # 创建dataset
    train_dataset = NumpyDataset(x=X_train, y=y_train)
    test_dataset = NumpyDataset(x=X_test, y=y_test)

    # 创建dataloader
    train_dataloader = DataLoader(
        dataset=train_dataset,
        batch_size=batch_size,  # 批次大小
        shuffle=True,  # 是否打乱提取数据的顺序，默认为False，表示不打乱；True就表示打乱顺序
        sampler=None,  # 主动给定shuffle产生的方式
        num_workers=0,  # 加载数据的线程数目，0表示直接在主线程中加载数据
        collate_fn=None,  # 给定如何将样本组合成批次数据
        pin_memory=False,  # 当GPU训练的时候，如果你的dataset中的数据没有经过数据转换的，将该参数设置为True的话可以减少cpu和gpu的数据传输
        drop_last=False,  # 如果最后一个批次的数据量小于batch_size,那么当前批次数据是否丢弃
        prefetch_factor=2
    )
    test_dataloader = DataLoader(
        dataset=test_dataset,
        batch_size=batch_size * 2,
        shuffle=False,
        num_workers=0,
        drop_last=False
    )

    return train_dataloader, test_dataloader


def t0():
    batch_size = 128
    total_epoch = 100
    # 1. 数据加载
    train_dataloader, test_dataloader = load_data(batch_size)

    # 4. 算法对象的创建
    net = SleepPositionClassify(num_classes=3)
    loss_fn = nn.CrossEntropyLoss()
    # opt = optim.SGD(params=net.parameters(), lr=0.001)
    opt = build_opt(net)

    # 5. 模型训练 BP的过程 --> 遍历训练数据集，进行模型参数更新
    for epoch in range(total_epoch):
        print(f"epoch is :{epoch} times")
        # 模型训练
        net.train()
        for x, y in train_dataloader:
            scores = net(x)  # 获取模型前向预测结果 [N,3]
            loss = loss_fn(scores, y)  # 求解损失
            opt.zero_grad()  # 将每个参数的梯度重置为0
            loss.backward()  # 求解每个参数的梯度值
            opt.step()  # 参数更新
    # 6. 模型评估
    with torch.no_grad():
        net.eval()
        y_preds = []
        y_trues = []
        for x, y in test_dataloader:
            scores = net(x)  # 获取模型前向预测结果 [N,3]
            y_pred = torch.argmax(scores, dim=1)  # [N,]
            y_trues.append(y)
            y_preds.append(y_pred)
        y_preds = torch.concat(y_preds, dim=0).numpy()
        y_trues = torch.concat(y_trues, dim=0).numpy()
        accuracy = accuracy_score(y_trues, y_preds)
        print("Accuracy:", accuracy)


if __name__ == "__main__":
    t0()