# -*- coding: utf-8 -*-

import numpy as np
import torch


class Corpus(object):
    BOS = '***'
    EOS = '$$$'
    UNK = 'UNKNOWN'

    def __init__(self, words, tags):
        self.words = words
        self.tags = tags

        self.wdict = {w: i for i, w in enumerate(self.words)}
        self.tdict = {t: i for i, t in enumerate(self.tags)}
        self.bi = self.wdict[self.BOS]
        self.ei = self.wdict[self.EOS]
        self.ui = self.wdict[self.UNK]
        self.nw = len(self.words)
        self.nt = len(self.tags)

    def load(self, fdata, window=5):
        data = []
        half = window // 2
        sentences = self.preprocess(fdata)
        for wordseq, tagseq in sentences:
            wis = [self.wdict[w] if w in self.wdict else self.ui
                   for w in wordseq]
            wis = [self.bi] * half + wis + [self.ei] * half
            tis = [self.tdict[t] if t in self.tdict else -1
                   for t in tagseq]
            x = torch.tensor([wis[i:i + window] for i in range(len(tis))],
                             dtype=torch.long)
            y = torch.tensor([ti for ti in tis], dtype=torch.long)
            data.append((x, y))
        return data

    def size(self):
        return self.nw - 3, self.nt

    @staticmethod
    def preprocess(fdata):
        start = 0
        sentences = []
        with open(fdata, 'r') as train:
            lines = [line for line in train]
        for i, line in enumerate(lines):
            if len(lines[i]) <= 1:
                splits = [l.split()[1:4:2] for l in lines[start:i]]
                wordseq, tagseq = zip(*splits)
                start = i + 1
                while start < len(lines) and len(lines[start]) <= 1:
                    start += 1
                sentences.append((wordseq, tagseq))
        return sentences

    @staticmethod
    def get_embed(fembed):
        with open(fembed, 'r') as f:
            lines = [line for line in f]
        splits = [line.split() for line in lines]
        words, embed = zip(*[
            (split[0], list(map(float, split[1:]))) for split in splits
        ])
        words = list(words)
        embed = torch.FloatTensor(embed)
        return words, embed
