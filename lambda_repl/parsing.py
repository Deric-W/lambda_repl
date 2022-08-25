#!/usr/bin/python3

"""Utilities for parsing lambda terms"""

from __future__ import annotations
from collections.abc import Sequence
from lambda_calculus.terms import Abstraction, Application, Term, Variable
from lark import Lark, Token
from lark.exceptions import UnexpectedInput, UnexpectedToken
from lark.visitors import Transformer, v_args

__all__ = (
    "PARSER",
    "LambdaTransformer"
)

PARSER = Lark.open_from_package(
    __name__,
    "grammar.lark",
    start="term",
    parser="lalr",
    propagate_positions=True
)


class LambdaTransformer(Transformer[Token, Term[str]]):
    """Transformer transforming an AST into a lambda term"""

    def transform_string(self, string: str) -> Term[str]:
        """parse a string and return the transformed lambda term"""
        match PARSER.parse(string):
            case Token(type="VARIABLE") as name:    # type: ignore
                return self.VARIABLE(name)
            case Token() as token:                  # type: ignore
                raise UnexpectedToken(token, {"VARIABLE",})
            case tree:
                return self.transform(tree)

    def __default__(self, data: object, children: object, meta: object) -> Term[str]:
        """handle unknown nodes"""
        raise UnexpectedInput(f"unknown node: {data}")

    def VARIABLE(self, name: Token) -> Variable[str]:
        """transform a variable node"""
        return Variable(name.value)

    @v_args(inline=True)
    def abstraction(self, variable: Variable[str], body: Term[str]) -> Abstraction[str]:
        """transform an abstraction"""
        return Abstraction(variable.name, body)

    def application(self, children: Sequence[Term[str]]) -> Application[str]:
        """transform an application"""
        return Application.with_arguments(children[0], children[1:])
