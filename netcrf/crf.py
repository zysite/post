# -*- coding: utf-8 -*-

import torch
import torch.nn as nn


class CRF(nn.Module):

    def __init__(self, nt):
        super(CRF, self).__init__()
        # 不同的词性个数
        self.nt = nt
        # 句间迁移
        self.trans = nn.Parameter(torch.randn(self.nt, self.nt))
        # 句首迁移
        self.BOS = nn.Parameter(torch.randn(self.nt))
        # 句尾迁移
        self.EOS = nn.Parameter(torch.randn(self.nt))

    def forward(self, emit, y):
        T = len(emit)
        alpha = self.BOS + emit[0]

        for i in range(1, T):
            scores = torch.transpose(self.trans + emit[i], 0, 1)
            alpha = logsumexp(scores + alpha, dim=1)
        logZ = logsumexp(alpha, dim=0)
        return logZ - self.score(emit, y)

    def score(self, emit, y):
        T = len(emit)

        score = torch.tensor(0, dtype=torch.float)
        score += self.BOS[y[0]]
        for i, (prev, ti) in enumerate(zip(y[:-1], y[1:])):
            score += self.trans[prev, ti] + emit[i, prev]
        score += self.EOS[y[-1]] + emit[-1, y[-1]]
        return score

    def viterbi(self, emit):
        T = len(emit)
        delta = torch.zeros(T, self.nt)
        paths = torch.zeros(T, self.nt, dtype=torch.long)

        delta[0] = self.BOS + emit[0]

        for i in range(1, T):
            scores = torch.transpose(self.trans + emit[i], 0, 1) + delta[i - 1]
            delta[i], paths[i] = torch.max(scores, dim=1)
        prev = torch.argmax(delta[-1])

        predict = [prev]
        for i in reversed(range(1, T)):
            prev = paths[i, prev]
            predict.append(prev)
        predict.reverse()
        return torch.tensor(predict)


def logsumexp(tensor, dim):
    # Find the max value along `dim`
    offset, _ = tensor.max(dim)
    # Make offset broadcastable
    broadcast = offset.unsqueeze(dim)
    # Perform log-sum-exp safely
    tmp = torch.log(torch.sum(torch.exp(tensor - broadcast), dim))
    # Add offset back
    return offset + tmp
