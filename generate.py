#!/usr/bin/env python

import torch
import os
import argparse
import json
import sys
import random

from helpers import *
from model import *


def generate(decoder, voc, rvoc, prime_str='A', predict_len=100,
             temperature=0.5, cuda=False):
    hidden = decoder.init_hidden(1)
    prime_input = Variable(char_tensor(rvoc, prime_str).unsqueeze(0))

    if cuda:
        hidden = hidden.cuda()
        prime_input = prime_input.cuda()
    predicted = prime_str

    # Use priming string to "build up" hidden state
    for p in range(len(prime_str) - 1):
        _, hidden = decoder(prime_input[:, p], hidden)

    inp = prime_input[:, -1]

    for p in range(predict_len):
        output, hidden = decoder(inp, hidden)

        # Sample from the network as a multinomial distribution
        output_dist = output.data.view(-1).div(temperature).exp()
        top_i = torch.multinomial(output_dist, 1)[0]

        # Add predicted character to string and use as next input
        predicted_char = voc[top_i]
        predicted += predicted_char
        inp = Variable(char_tensor(rvoc, predicted_char).unsqueeze(0))
        if cuda:
            inp = inp.cuda()

    return predicted[len(prime_str):]

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-l', '--predict_len', type=int, default=100)
    argparser.add_argument('-t', '--temperature', type=float, default=0.8)
    argparser.add_argument('-c', '--count', type=int, default=100)
    argparser.add_argument('--cuda', action='store_true')
    args = argparser.parse_args()

    generate_count = args.count
    del args.count

    voc = open('./model/voc.bin', 'rt').read()
    rvoc = dict(reversed(t) for t in enumerate(voc))
    kwdict = json.load(open('model/dict.json', 'rt'))
    decoder = torch.load('model/weights.pt')

    for iteration in range(generate_count):
        sys.stderr.write(str(iteration) + '\n')

        random_garbage = [voc[random.randint(0, len(voc) - 1)]
                          for _ in range(100)]
        random_garbage.extend(['\1', '\n'])
        random_garbage = ''.join(random_garbage)

        sent = generate(decoder, voc, rvoc,
                        prime_str=random_garbage,
                        **vars(args))

        if '\1' not in sent:
            continue

        sent = sent[:sent.rfind('\1')] + '\1\n'

        import re
        res = []
        i = 0
        for m in re.finditer('k(\d+)', sent):
            res.append(sent[i:m.span()[0]])
            key = m.group(0)
            if key in kwdict:
                res.append(kwdict[key])
            else:
                res.append(m.group(0))
            i = m.span()[1]
        res.append(sent[i:])
        sent = ''.join(res)
        print(sent)
