#!/usr/bin/python3

"""Tests for lambda term parsing"""

from unittest import TestCase
from lambda_calculus.terms import Variable, Abstraction, Application
from lark import Token
from lambda_repl import parsing


class ParsingTest(TestCase):
    """Test for the term parser and transformer"""

    transformer: parsing.LambdaTransformer

    def setUp(self) -> None:
        """create a transformer"""
        self.transformer = parsing.LambdaTransformer()

    def test_example(self) -> None:
        """test lambda_calculus example"""
        x = Variable("x")
        y = Variable("y")
        term = Variable("+") \
            .apply_to(x, y) \
            .abstract("x", "y") \
            .apply_to(y, Variable("3")) \
            .abstract("y") \
            .apply_to(Variable("4"))
        self.assertEqual(
            self.transformer.transform_string("(λy.(λx.(λy. + x y)) y 3) 4"),
            term
        )

    def test_whitespace(self) -> None:
        """test allowed whitespace"""
        self.assertEqual(
            self.transformer.transform_string("a      \t  b"),
            Application(Variable("a"), Variable("b"))
        )
        self.assertEqual(
            self.transformer.transform_string("λ   a    \t. \t    b"),
            Abstraction("a", Variable("b"))
        )
        self.assertEqual(
            self.transformer.transform_string("a (   λ  a  . b ) c"),
            Application.with_arguments(
                Variable("a"),
                (Abstraction("a", Variable("b")), Variable("c"))
            )
        )

    def test_variables(self) -> None:
        """test valid variable names"""
        for name in ("x", "1", "1x", "hi!", "ähm-hi?"):
            self.assertEqual(
                self.transformer.transform_string(f"λ{name}.{name}"),
                Abstraction(name, Variable(name))
            )

    def test_application(self) -> None:
        """test application order"""
        self.assertEqual(
            self.transformer.transform_string("a b c"),
            Variable("a").apply_to(Variable("b"), Variable("c"))
        )

    def test_abstraction(self) -> None:
        """test abstraction parsing"""
        self.assertEqual(
            self.transformer.transform_string("λa.λb.a b c"),
            Variable("a")
                .apply_to(Variable("b"), Variable("c"))
                .abstract("a", "b")
        )

    def test_brackets(self) -> None:
        """test bracket parsing"""
        self.assertEqual(
            self.transformer.transform_string("(a)"),
            Variable("a")
        )
        self.assertEqual(
            self.transformer.transform_string("(a b) (c d)"),
            Application(
                Application(
                    Variable("a"),
                    Variable("b")
                ),
                Application(
                    Variable("c"),
                    Variable("d")
                )
            )
        )
        self.assertEqual(
            self.transformer.transform_string("λa.(λb.a) b c"),
            Abstraction("b", Variable("a"))
                .apply_to(Variable("b"), Variable("c"))
                .abstract("a")
        )
        self.assertEqual(
            self.transformer.transform_string("(λa.a) λb.b"),
            Application(
                Abstraction("a", Variable("a")),
                Abstraction("b", Variable("b"))
            )
        )

    def test_backslash(self) -> None:
        """test lambda alternative"""
        self.assertEqual(
            self.transformer.transform_string(r"\a.a"),
            Abstraction("a", Variable("a"))
        )


class PostLexTest(TestCase):
    """Tests for WhitespacePostLex"""

    postlex: parsing.WhitespacePostLex

    def setUp(self) -> None:
        """create a PostLex"""
        self.postlex = parsing.WhitespacePostLex()

    def test_no_whitespace(self) -> None:
        """test handling of tokens other than whitespace"""
        tokens = (
            Token("BACKLASH", "\\"),
            Token("VARIABLE", "a"),
            Token("DOT", "."),
            Token("LPAR", "("),
            Token("VARIABLE", "a"),
            Token("RPAR", ")")
        )
        self.assertEqual(
            tuple(self.postlex.process(iter(tokens))),
            tokens
        )

    def test_abstraction_unnecessary(self) -> None:
        """test handling of unnecessary whitespace in abstractions"""
        tokens = (
            Token("BACKLASH", "λ"),
            Token("_WHITESPACE", " "),
            Token("VARIABLE", "a"),
            Token("_WHITESPACE", "\t"),
            Token("DOT", "."),
            Token("_WHITESPACE", "  "),
            Token("LPAR", "("),
            Token("VARIABLE", "a"),
            Token("RPAR", ")")
        )
        self.assertEqual(
            tuple(self.postlex.process(iter(tokens))),
            (
                Token("BACKLASH", "λ"),
                Token("VARIABLE", "a"),
                Token("DOT", "."),
                Token("LPAR", "("),
                Token("VARIABLE", "a"),
                Token("RPAR", ")")
            )
        )

    def test_backslash_unnecessary(self) -> None:
        """test handling of unnecessary whitespace in abstractions with a backslash"""
        tokens = (
            Token("BACKLASH", "\\"),
            Token("_WHITESPACE", " "),
            Token("VARIABLE", "a"),
            Token("_WHITESPACE", "\t"),
            Token("DOT", "."),
            Token("_WHITESPACE", "  "),
            Token("LPAR", "("),
            Token("VARIABLE", "a"),
            Token("RPAR", ")")
        )
        self.assertEqual(
            tuple(self.postlex.process(iter(tokens))),
            (
                Token("BACKLASH", "\\"),
                Token("VARIABLE", "a"),
                Token("DOT", "."),
                Token("LPAR", "("),
                Token("VARIABLE", "a"),
                Token("RPAR", ")")
            )
        )

    def test_brackets_unnecessary(self) -> None:
        """test handling of unnecessary whitespace in brackets"""
        tokens = (
            Token("BACKLASH", "\\"),
            Token("VARIABLE", "a"),
            Token("DOT", "."),
            Token("LPAR", "("),
            Token("_WHITESPACE", "\t"),
            Token("VARIABLE", "a"),
            Token("_WHITESPACE", "  "),
            Token("RPAR", ")")
        )
        self.assertEqual(
            tuple(self.postlex.process(iter(tokens))),
            (
                Token("BACKLASH", "\\"),
                Token("VARIABLE", "a"),
                Token("DOT", "."),
                Token("LPAR", "("),
                Token("VARIABLE", "a"),
                Token("RPAR", ")")
            )
        )

    def test_ends_unnecessary(self) -> None:
        """test handling of unnecessary whitespace at the start and end"""
        tokens = (
            Token("_WHITESPACE", "\t"),
            Token("VARIABLE", "a"),
            Token("_WHITESPACE", " ")
        )
        self.assertEqual(
            tuple(self.postlex.process(iter(tokens))),
            (tokens[1],)
        )

    def test_necessary(self) -> None:
        """test handling of necessary whitespace"""
        tokens = (
            Token("VARIABLE", "a"),
            Token("_WHITESPACE", "\t"),
            Token("VARIABLE", "a")
        )
        self.assertEqual(
            tuple(self.postlex.process(iter(tokens))),
            tokens
        )
