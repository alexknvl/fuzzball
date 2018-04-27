# fuzzball
Scala fuzzer. [~44 bugs found in Dotty](https://github.com/lampepfl/dotty/issues/4389).

> Code is slower and uglier than it needs be. Such is life.

## Installing
```
pip3 install torch torchvision numpy tqdm argparse
```

## Running
```
python3.5 -u ./generate.py --temperature 1.0 --count 30 --predict_len 3000 > out.txt
python3.5 postprocess.py --samples 3 --maxids 8 out.txt results/
```

## Examples
Some snippets generated by the fuzzer:
```scala
abstract class i0[+I1] {
def +[I2[I2]: i0[_], i3 <: I2[I2]] = (???) :: i3
val I4 = new i6
val i6: i6 = I5
i6
}

object Boolean {}
trait I0[I0]
object I1 {
def I1[I0](I1: => Int, I2: I1 { type I1 <: I0[I2] } with I0.I0[_]#I0[I1] = new I0[I1])#i3#i3 = new I0[I1] {}
}

abstract class I0() {
val I1 = 1 + 1; case (I1: Nil) => 1;
case Some(I1) =>
I1
}.isInstanceOf[Option][String]{ new I0();
val I1 = ;
def I1: Int = 0 { i3 =>
final def i2: Int => Any = I1
}
}
```
Note that not all snippets will properly parse, and the vast majority of them won't typecheck. It will generate a limited subset of Scala (roughly Scala2 with some Dotty-specific keywords here and there).

## Testing on dotty

Add a new test to `CompilationTests` containing:
```scala
compileFilesInDir("path/to/the/output/files", defaultOptions)
```

and run it using `testOnly` from the `sbt` console.

Optionally, find `compiler/src/dotty/tools/dotc/Run.scala` and add:
```scala
case ex @ (_: StackOverflowError | _: ClassCastException) =>
  ctx.echo(i"exception occurred while compiling $units%, %")
  throw ex
```
to print more stack traces.

## Credits
Code was partially derived from https://github.com/spro/char-rnn.pytorch. See `char-rnn.pytorch_LICENSE` for the original license.
