#!/usr/bin/env python3.5

import torch
import torch.nn as nn
from torch.autograd import Variable
import argparse
import os

from tqdm import tqdm

from helpers import *
from model import *
from generate import *

# Parse command line arguments
argparser = argparse.ArgumentParser()

argparser.add_argument('vocabulary', type=str)
argparser.add_argument('source', type=str)

argparser.add_argument('--model', type=str, default="lstm")
argparser.add_argument('--n_epochs', type=int, default=2000)
argparser.add_argument('--print_every', type=int, default=10)
argparser.add_argument('--hidden_size', type=int, default=100)
argparser.add_argument('--n_layers', type=int, default=3)
argparser.add_argument('--learning_rate', type=float, default=0.01)
argparser.add_argument('--temperature', type=float, default=0.9)
argparser.add_argument('--chunk_len', type=int, default=1000)
argparser.add_argument('--batch_size', type=int, default=16)
argparser.add_argument('--shuffle', action='store_true')
argparser.add_argument('--cuda', action='store_true')
args = argparser.parse_args()

if args.cuda:
    print("Using CUDA")

file, file_len, voc, rvoc = read_file(args.source)
fragments = file.split('\n\1\n')

def random_training_set(chunk_len, batch_size):
    input  = torch.LongTensor(batch_size, chunk_len)
    target = torch.LongTensor(batch_size, chunk_len)

    for bi in range(batch_size):
        random.shuffle(fragments)
        file = '\n\1\n'.join(fragments)
        chunk   = file[0:chunk_len+1]

        i = 0
        while i < chunk_len:
            j = chunk.find('\1', i)
            if j == -1:
                j = chunk_len
            i = j + 1

        input[bi]  = char_tensor(rvoc, chunk[:-1])
        target[bi] = char_tensor(rvoc, chunk[1:])

    input  = Variable(input)
    target = Variable(target)

    if args.cuda:
        input = input.cuda()
        target = target.cuda()
    return input, target

def train(inp, target):
    hidden = decoder.init_hidden(args.batch_size)
    if args.cuda:
        hidden = hidden.cuda()
    decoder.zero_grad()
    loss = 0

    for c in range(args.chunk_len):
        output, hidden = decoder(inp[:,c:c+1], hidden)
        loss += criterion(output.view(args.batch_size, -1), target[:,c])

    loss.backward()
    decoder_optimizer.step()

    return loss.data[0] / args.chunk_len

def save():
    save_filename = os.path.splitext(os.path.basename(args.source))[0] + '.pt'
    torch.save(decoder, save_filename)
    print('Saved as %s' % save_filename)

def load_maybe():
    save_filename = os.path.splitext(os.path.basename(args.source))[0] + '.pt'
    if os.path.exists(save_filename):
        print('Loading %s' % save_filename)
        return torch.load(save_filename)
    else:
        return None

# Initialize models and start training

decoder = load_maybe()
if decoder is None:
    decoder = CharRNN(
        input_size=len(voc),
        hidden_size=args.hidden_size,
        output_size=len(voc),
        model=args.model,
        n_layers=args.n_layers,
    )
print(decoder.input_size, decoder.hidden_size, decoder.output_size, decoder.n_layers)
decoder_optimizer = torch.optim.Adam(
    decoder.parameters(),
    lr=args.learning_rate,
    betas=(0.99, 0.9999))
criterion = nn.CrossEntropyLoss()

if args.cuda:
    decoder.cuda()

start = time.time()
all_losses = []
loss_avg = 0

import json
DICT = json.load(open(args.vocabulary, 'rt'))

try:
    print("Training for %d epochs..." % args.n_epochs)
    for epoch in tqdm(range(1, args.n_epochs + 1)):
        loss = train(*random_training_set(args.chunk_len, args.batch_size))
        eta = 0.9 if epoch > 1 else 0

        loss_avg = eta * loss_avg + (1 - eta) * loss

        print(loss_avg)

        if epoch % args.print_every == 0:
            print('[%s (%d %d%%) %.4f]' % (
                time_since(start), epoch,
                epoch / args.n_epochs * 100, loss_avg))
            sent = generate(
                decoder, voc, rvoc, '\1\n', 400,
                temperature=args.temperature, cuda=args.cuda)
            import re
            res = []
            i = 0
            for m in re.finditer('k(\d+)', sent):
                res.append(sent[i:m.span()[0]])
                key = m.group(0)
                if key in DICT:
                    res.append(DICT[key])
                else:
                    res.append(m.group(0))
                i = m.span()[1]
            res.append(sent[i:])
            sent = ''.join(res)
            print(sent, '\n')

    print("Saving...")
    save()

except KeyboardInterrupt:
    print("Saving before quit...")
    save()

