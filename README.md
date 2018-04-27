# fuzzball
Scala fuzzer

## Installing
```
pip3 install torch torchvision numpy tqdm argparse
```

## Running
```
python3.5 -u ./generate.py --temperature 1.0 --count 30 --predict_len 3000 train.txt > out.txt
python3.5 postprocess.py out.txt results/
```

## Credits
Code was partially derived from https://github.com/spro/char-rnn.pytorch. See `char-rnn.pytorch_LICENSE` for the original license.
