import time
import math
import torch


def read_file(filename):
    file = open(filename, 'rt').read()
    voc = sorted(set(file))
    rvoc = dict(reversed(t) for t in enumerate(voc))
    # n_characters = len(all_characters)
    return file, len(file), voc, rvoc


def char_tensor(rvoc, string):
    tensor = torch.zeros(len(string)).long()
    for c in range(len(string)):
        tensor[c] = rvoc[string[c]]
    return tensor


def time_since(since):
    s = time.time() - since
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)

