#!/usr/bin/python3

"""Alias implementations"""

from __future__ import annotations
from abc import abstractmethod
from collections import OrderedDict
from collections.abc import MutableMapping, Iterator
from typing import TypeVar, Type
from lambda_calculus.terms import Term
from lambda_calculus.visitors.substitution import Substitution

__all__ = (
    "Aliases",
    "LetAliases"
)

V = TypeVar("V")


class Aliases(MutableMapping[V, Term[V]]):
    """ABC for alias implementations"""

    __slots__ = ()

    @abstractmethod
    def apply(self, term: Term[V]) -> Term[V]:
        """apply the aliases to a term"""
        raise NotImplementedError()


class LetAliases(Aliases[V]):
    """Alias implementations with no self reference"""

    aliases: OrderedDict[V, Term[V]]

    substitution: Type[Substitution[V]]

    __slots__ = (
        "aliases",
        "substitution"
    )

    def __init__(self, substitution: Type[Substitution[V]]) -> None:
        self.aliases = OrderedDict()
        self.substitution = substitution

    def __len__(self) -> int:
        return len(self.aliases)

    def __iter__(self) -> Iterator[V]:
        return iter(self.aliases)

    def __getitem__(self, alias: V) -> Term[V]:
        return self.aliases[alias]

    def __setitem__(self, alias: V, term: Term[V]) -> None:
        self.aliases[alias] = self.apply(term)
        self.aliases.move_to_end(alias, last=True)

    def __delitem__(self, alias: V) -> None:
        del self.aliases[alias]

    def apply(self, term: Term[V]) -> Term[V]:
        """apply the aliases to a term"""
        # dont substitute free variables with later defined aliases
        for alias, value in reversed(self.aliases.items()):
            term = term.accept(self.substitution.from_substitution(alias, value))
        return term
