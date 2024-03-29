import torch
import torch.nn as nn
import math

class InputEmbeddings(nn.Module):
   
    def __init__(self, d_model: int, vocab_size: int):
        super().__init__() 
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.embedding = nn.Embedding(vocab_size, d_model)

    def forward(self, x): 
        return self.embedding(x) * math.sqrt(self.d_model)

class PositionalEncoding(nn.Module):

    def __init__(self, d_model: int, seq_len: int, dropout: float) -> None:
        super().__init__()
        self.d_model = d_model
        self.seq_len = seq_len
        self.dropout = nn.Dropout(dropout)

        # matrix of shape (seq_len, d_model) 
        pe = torch.zeros(seq_len, d_model) 
        # vector of shape (seq_len, 1) 
        position = torch.arange(0, seq_len, dtype=torch.float).unsqueeze(1) 
        # formula for positional encoding
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)) 
        pe[:, 0::2] = torch.sin(position * div_term) # even indices
        pe[:, 1::2] = torch.cos(position * div_term) # odd indices

        pe = pe.unsqueeze(0)

        self.register_buffer('pe', pe) # register pe as a buffer to be used in forward pass

    def forward(self, x):  
        x = x + (self.pe[:, :x.shape(1), :]).requires_grad_(False) # (batch_size, seq_len, d_model)
        return self.dropout(x)
    
class LayerNormalization(nn.Module):

    def __init__(self, eps:float = 10**-6) -> None:
        super().__init__()
        self.eps = eps
        self.alpha = nn.Parameter(torch.ones(1)) # Mul
        self.bias = nn.Parameter(torch.zeros(1)) # Add

    def forward(self, x):
        mean = x.mean(dim = -1, keepdim=True)
        std = x.std(dim = -1, keepdim=True)
        return self.alpha * (x - mean) / (std + self.eps) + self.bias
    
class FeedForwardBlock(nn.Module):

    def __init__(self, d_model: int, d_ff: int, dropout: float) -> None:
        super().__init__()
        self.linear_1 == nn.Linear(d_model, d_ff) # matrix W1 and B1
        self.dropout = nn.Dropout(dropout)
        self.linear_2 == nn.Linear(d_ff, d_model) # matrix W2 and B2

    def forward(self, x):
        # (Batch_size, seq_len, d_model) --> (Batch_size, seq_len, d_ff) --> (Batch_size, seq_len, d_model)
        return self.linear_2(self.dropout(torch.relu(self.linear_1(x))))