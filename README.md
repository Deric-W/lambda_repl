# lambda_repl

![Tests](https://github.com/Deric-W/lambda_repl/actions/workflows/Tests.yaml/badge.svg)
[![codecov](https://codecov.io/gh/Deric-W/lambda_repl/branch/main/graph/badge.svg?token=SU3982mC17)](https://codecov.io/gh/Deric-W/lambda_repl)

The `lambda_repl` package contains a [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop)
for the [lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus).

To use it, execute `lambda-repl` or `python3 -m lambda_repl` and enter commands.

## Requirements

Python >= 3.10 and the packages [`lambda_calculus`](https://github.com/Deric-W/lambda_calculus)
and [`lark`](https://github.com/lark-parser/lark) are required to use this package.

## Installation

```sh
python3 -m pip install lambda-repl
```

## Examples

```
python3 -m lambda_repl
Welcome to the the Lambda REPL, type 'help' for help
λ alias I = \x.x
λ alias K = λx.λy.x
λ import SUCC = lambda_calculus.terms.arithmetic.SUCCESSOR
λ aliases
I = (λx.x)
K = (λx.(λy.x))
SUCC = (λn.(λf.(λx.(f ((n f) x)))))
λ trace K a b
β ((λy.a) b)
β a
λ exit
Exiting REPL...
```
