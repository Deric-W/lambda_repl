#!/usr/bin/python3

"""CLI entry point utilities"""

from argparse import ArgumentParser, Namespace, FileType
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor
from lambda_calculus.visitors.substitution.renaming import CountingSubstitution
from . import LambdaREPL, __doc__ as description, __version__
from .aliases import LetAliases
from .parsing import LambdaTransformer

__all__ = (
    "ARGUMENT_PARSER",
    "main",
    "main_cli"
)

ARGUMENT_PARSER = ArgumentParser(description=description)
ARGUMENT_PARSER.add_argument(
    "-v",
    "--version",
    action="version",
    version=f"%(prog)s {__version__}"
)
ARGUMENT_PARSER.add_argument(
    "-f",
    "--file",
    type=FileType("r"),
    action="append",
    help="add file which should be executed in the REPL"
)


def main(args: Namespace) -> int:
    """Entry point for the REPL"""
    repl = LambdaREPL(
        LetAliases(CountingSubstitution),
        LambdaTransformer(),
        BetaNormalisingVisitor()
    )
    for file in args.file or ():
        for line in file:
            repl.cmdqueue.append(line)
    repl.cmdloop()
    return 0


def main_cli() -> int:
    """CLI entry point"""
    return main(ARGUMENT_PARSER.parse_args())
