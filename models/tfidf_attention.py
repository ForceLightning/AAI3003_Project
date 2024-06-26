"""TfIdf-based Attention model.
"""

import torch
from torch import nn
from torch.nn.utils.parametrizations import weight_norm


class TfIdfAttention(nn.Module):
    """An attention model for TfIdf features.

    :param n_inputs: Number of input channels.
    :type n_inputs: int
    :param n_outputs: Number of output channels.
    :type n_outputs: int
    :param embed_size: Attention embedding size.
    :type embed_size: int
    :param hidden_size: Hidden layer sizes.
    :type hidden_size: list[int]
    :param n_heads: Number of attention heads.
    :type n_heads: int
    :param dropout: Dropout rate.
    :type dropout: float
    """

    def __init__(
        self,
        n_inputs: int,
        n_outputs: int,
        embed_size: int,
        hidden_size: list[int],
        n_heads: int,
        dropout: float,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        embed_dim = n_heads * embed_size
        assert (
            embed_dim == n_inputs
        ), "n_inputs must be divisible by n_heads * embed_size"
        self.attention = nn.MultiheadAttention(
            embed_dim, n_heads, dropout=dropout, batch_first=True
        )
        layers = []
        self.relu = nn.Mish()
        self.dropout = nn.Dropout(dropout)
        for i, hidden in enumerate(hidden_size):
            if i == 0:
                fc = weight_norm(nn.Linear(embed_dim, hidden))
                self.fc = fc
            else:
                fc = weight_norm(nn.Linear(hidden_size[i - 1], hidden))
                setattr(self, f"fc{i}", fc)
            layers.append(fc)
            layers.append(self.relu)
            layers.append(self.dropout)

        self.final_fc = weight_norm(nn.Linear(hidden_size[-1], n_outputs))
        layers.append(self.final_fc)
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        x, _ = self.attention(x, x, x)
        x = self.net(x)
        x = x.squeeze()
        return x


class TfIdfDense(nn.Module):
    """A dense model for TfIdf features.

    :param n_inputs: Number of input channels.
    :type n_inputs: int
    :param n_outputs: Number of output channels.
    :type n_outputs: int
    :param hidden_size: Hidden layer sizes.
    :type hidden_size: list[int]
    :param dropout: Dropout rate.
    :type dropout: float
    """

    def __init__(
        self,
        n_inputs: int,
        n_outputs: int,
        hidden_size: list[int],
        dropout: float,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        layers = []
        self.activation = nn.Mish()
        self.dropout = nn.Dropout(dropout)
        for i, hidden in enumerate(hidden_size):
            if i == 0:
                fc = weight_norm(nn.Linear(n_inputs, hidden))
                self.fc = fc
            else:
                fc = weight_norm(nn.Linear(hidden_size[i - 1], hidden))
                setattr(self, f"fc{i}", fc)
            layers.append(fc)
            layers.append(self.activation)
            layers.append(self.dropout)
        self.final_fc = weight_norm(nn.Linear(hidden_size[-1], n_outputs))
        layers.append(self.final_fc)
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        x = self.net(x)
        return x
