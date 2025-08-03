
import torch
import torch.nn as nn

class TwoLayerLSTM(nn.Module):
    def __init__(self, input_size=2, hidden_size=64, num_layers=2, output_size=2, dropout=0.0):
        super(TwoLayerLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=64,
                            num_layers=num_layers, batch_first=True, dropout=dropout)
        self.linear = nn.Linear(64, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        out = self.linear(lstm_out)
        return out
