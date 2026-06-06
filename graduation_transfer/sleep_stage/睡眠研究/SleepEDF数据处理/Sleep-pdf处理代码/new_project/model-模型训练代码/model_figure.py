from torchviz import make_dot
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score


class SleepRNNLSTM(nn.Module):
    def __init__(self, input_size, rnn_hidden_size, lstm_hidden_size, num_layers, num_classes):
        super(SleepRNNLSTM, self).__init__()

        self.rnn_hidden_size = rnn_hidden_size
        self.lstm_hidden_size = lstm_hidden_size
        self.num_layers = num_layers

        # ① RNN 层
        self.rnn = nn.RNN(
            input_size=input_size,
            hidden_size=rnn_hidden_size,
            num_layers=1,
            batch_first=True,
            nonlinearity='tanh'
        )

        # ② LSTM 层
        self.lstm = nn.LSTM(
            input_size=rnn_hidden_size,
            hidden_size=lstm_hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )

        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(lstm_hidden_size, num_classes)

    def forward(self, x):
        batch_size = x.size(0)

        # RNN 初始隐藏状态
        h0_rnn = torch.zeros(1, batch_size, self.rnn_hidden_size).to(x.device)

        # LSTM 初始状态
        h0_lstm = torch.zeros(self.num_layers, batch_size, self.lstm_hidden_size).to(x.device)
        c0_lstm = torch.zeros(self.num_layers, batch_size, self.lstm_hidden_size).to(x.device)

        # ① RNN
        rnn_out, _ = self.rnn(x, h0_rnn)
        # rnn_out: (batch, seq_len, rnn_hidden_size)

        # ② LSTM
        lstm_out, _ = self.lstm(rnn_out, (h0_lstm, c0_lstm))
        # lstm_out: (batch, seq_len, lstm_hidden_size)

        out = self.dropout(lstm_out[:, -1, :])
        out = self.fc(out)
        return out

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SleepRNNLSTM(
    input_size=10,
    rnn_hidden_size=32,
    lstm_hidden_size=64,
    num_layers=2,
    num_classes=4
).to(device)


