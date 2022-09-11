#!/usr/bin/python3

"""REPL for the lambda calculus"""

from __future__ import annotations
from cmd import Cmd
from typing import Any
from lambda_calculus.terms import Term
from lambda_calculus.visitors.normalisation import (
    Conversion,
    BetaNormalisingVisitor
)
from lark.exceptions import UnexpectedInput
from .parsing import LambdaTransformer
from .aliases import Aliases

__version__ = "1.1.0"
__author__  = "Eric Niklas Wolf"
__email__   = "eric_niklas.wolf@mailbox.tu-dresden.de"
__all__ = (
    "LambdaREPL",
    "aliases",
    "main",
    "parsing"
)


class LambdaREPL(Cmd):
    """interactive REPL"""

    aliases: Aliases[str]

    transformer: LambdaTransformer

    visitor: BetaNormalisingVisitor

    def __init__(self, aliases: Aliases[str], transformer: LambdaTransformer, visitor: BetaNormalisingVisitor, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.aliases = aliases
        self.transformer = transformer
        self.visitor = visitor
        self.intro = "Welcome to the the Lambda REPL, type 'help' for help"
        self.prompt = "λ "

    def parse_term(self, term: str) -> Term[str] | None:
        """parse a term and handle error display"""
        try:
            return self.transformer.transform_string(term)
        except UnexpectedInput as error:
            self.stdout.write(f"Error while parsing: {error}")
            self.stdout.write(error.get_context(term))
        return None

    def emptyline(self) -> bool:
        """ignore empty lines"""
        return False

    def default(self, line: str) -> None:
        """print an error"""
        self.stdout.write(f"*** Unknown command: {line}\n")

    def do_trace(self, arg: str) -> bool:
        """trace the evaluation of a lambda term"""
        term = self.parse_term(arg)
        if term is not None:
            term = self.aliases.apply(term)
            for conversion, step in term.accept(self.visitor):
                if conversion is Conversion.ALPHA:
                    symbol = "α"
                elif conversion is Conversion.BETA:
                    symbol = "β"
                else:
                    symbol = "?"    # type: ignore[unreachable]
                self.stdout.write(f"{symbol} {step}\n")
        return False

    def do_evaluate(self, arg: str) -> bool:
        """evaluate a lambda term"""
        term = self.parse_term(arg)
        if term is not None:
            term = self.aliases.apply(term)
            self.stdout.write(f"{self.visitor.skip_intermediate(term)}\n")
        return False

    do_eval = do_evaluate

    def do_alias(self, arg: str) -> bool:
        """define an alias for a lambda term with name = term"""
        match arg.partition("="):
            case (alias, "=", value):
                term = self.parse_term(value)
                if term is not None:
                    self.aliases[alias.strip()] = term
            case _:
                self.stdout.write("invalid Command: missing alias value\n")
        return False

    def do_aliases(self, _: object) -> bool:
        """list defined aliases"""
        for alias, term in self.aliases.items():
            self.stdout.write(f"{alias} = {term}\n")
        return False

    def do_clear(self, arg: str) -> bool:
        """clear all aliases or a specific one"""
        alias = arg.strip()
        if alias:
            try:
                del self.aliases[alias]
            except KeyError:
                self.stdout.write(f"Error: alias '{alias}' does not exist\n")
        else:
            self.aliases.clear()
        return False

    def do_exit(self, _: object) -> bool:
        """exit the repl"""
        self.stdout.write("Exiting REPL...\n")
        return True

    do_EOF = do_exit
