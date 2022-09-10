#!/usr/bin/python3

"""Tests for alias implementations"""

from unittest import TestCase
from lambda_calculus.terms import Variable
from lambda_calculus.visitors.substitution.renaming import CountingSubstitution
from lambda_repl import aliases


class LetAliasesTest(TestCase):
    """Test for alias implementation without self reference"""

    aliases: aliases.LetAliases[str]

    def setUp(self) -> None:
        """create empty aliases"""
        self.aliases = aliases.LetAliases(CountingSubstitution)

    def test_set(self) -> None:
        """test setting new aliases"""
        self.aliases["a"] = Variable("1")
        self.aliases["b"] = Variable("a").apply_to(Variable("c"))
        self.aliases["c"] = Variable("2")
        self.assertEqual(
            list(self.aliases.items()),
            [
                ("a", Variable("1")),
                ("b", Variable("1").apply_to(Variable("c"))),
                ("c", Variable("2"))
            ]
        )

    def test_override(self) -> None:
        """test overriding aliases"""
        self.aliases["a"] = Variable("1")
        self.aliases["b"] = Variable("a").apply_to(Variable("c"))
        self.aliases["a"] = Variable("2")
        self.assertEqual(
            list(self.aliases.items()),
            [
                ("b", Variable("1").apply_to(Variable("c"))),
                ("a", Variable("2"))
            ]
        )

    def test_apply(self) -> None:
        """test applying aliases"""
        self.aliases["a"] = Variable("1")
        self.aliases["b"] = Variable("a").apply_to(Variable("c"))
        self.aliases["a"] = Variable("2")
        self.aliases["c"] = Variable("3")
        self.assertEqual(
            self.aliases.apply(
                Variable("a").apply_to(Variable("b"), Variable("c"))
            ),
            Variable("2").apply_to(
                Variable("1").apply_to(Variable("c")), Variable("3")
            )
        )

    def test_self_reference(self) -> None:
        """test handling of self references"""
        self.aliases["a"] = Variable("a").apply_to(Variable("b"))
        self.assertEqual(
            self.aliases["a"],
            Variable("a").apply_to(Variable("b"))
        )
