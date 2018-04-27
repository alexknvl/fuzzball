# fuzzball
Scala fuzzer

Code is probably slower and uglier than it needs be. Such is life.

## Installing
```
pip3 install torch torchvision numpy tqdm argparse
```

## Running
```
python3.5 -u ./generate.py --temperature 1.0 --count 30 --predict_len 3000 train.txt > out.txt
python3.5 postprocess.py --samples 3 --maxids 8 out.txt results/
```

## Testing on dotty

Add a new test to `CompilationTests` containing:
```scala
compileFilesInDir("path/to/the/output/files", defaultOptions)
```

and run it using `testOnly` from the `sbt` console.

Optionally, find `compiler/src/dotty/tools/dotc/Run.scala` and add:
```
case ex @ (_: StackOverflowError | _: ClassCastException) =>
  ctx.echo(i"exception occurred while compiling $units%, %")
  throw ex
```
to print more stack traces.

## Credits
Code was partially derived from https://github.com/spro/char-rnn.pytorch. See `char-rnn.pytorch_LICENSE` for the original license.
