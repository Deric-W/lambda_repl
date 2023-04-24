#!/usr/bin/python3

"""Tests for the REPL"""

from io import StringIO
from unittest import TestCase
from lambda_calculus.terms import Variable
from lambda_calculus.terms.arithmetic import SUCCESSOR
from lambda_calculus.visitors.substitution.renaming import CountingSubstitution
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor
from lambda_repl import LambdaREPL
from lambda_repl.aliases import LetAliases
from lambda_repl.parsing import LambdaTransformer


class REPLTest(TestCase):
    """Test for the REPL"""

    repl: LambdaREPL

    stdin: StringIO

    stdout: StringIO

    def setUp(self) -> None:
        """create a REPL"""
        self.stdin = StringIO()
        self.stdout = StringIO()
        self.repl = LambdaREPL(
            LetAliases(CountingSubstitution),
            LambdaTransformer(),
            BetaNormalisingVisitor(),
            stdin=self.stdin,
            stdout=self.stdout
        )
        self.repl.use_rawinput = False

    def test_empty(self) -> None:
        """test handling of empty lines"""
        self.assertFalse(self.repl.onecmd(""))
        self.assertEqual(self.stdout.getvalue(), "")

    def test_evaluate(self) -> None:
        """test evaluating terms"""
        self.assertFalse(self.repl.onecmd(r"evaluate (\x.\y.x) a b"))
        self.assertEqual(
            self.stdout.getvalue(),
            "a\n"
        )

    def test_eval(self) -> None:
        """test eval alias"""
        self.assertFalse(self.repl.onecmd(r"eval (\x.\y.x) a b"))
        self.assertEqual(
            self.stdout.getvalue(),
            "a\n"
        )

    def test_trace(self) -> None:
        """test tracing term evaluation"""
        self.assertFalse(self.repl.onecmd(r"trace (\x.\y.x) a b"))
        self.assertEqual(
            self.stdout.getvalue(),
            "β ((λy.a) b)\nβ a\n"
        )

    def test_syntax_error(self) -> None:
        """test handling of syntax errors while parsing"""
        self.assertFalse(self.repl.onecmd(r"eval (\x.\y.x) a b."))
        self.assertTrue(self.stdout.getvalue().startswith("Error while parsing: "))
        self.assertTrue(self.stdout.getvalue().endswith("\n"))

    def test_alias(self) -> None:
        """test setting aliases"""
        self.assertFalse(self.repl.onecmd("alias a = b c"))
        self.assertEqual(
            self.repl.aliases,
            {
                "a": Variable("b").apply_to(Variable("c"))
            }
        )

    def test_invalid_alias(self) -> None:
        """test handling invalid aliases"""
        self.assertFalse(self.repl.onecmd("alias a = b c."))
        self.assertEqual(self.repl.aliases, {})
        self.assertTrue(self.stdout.getvalue().startswith("Error while parsing: "))
        self.assertTrue(self.stdout.getvalue().endswith("\n"))

    def test_no_alias_value(self) -> None:
        """test handling missing alias values"""
        self.assertFalse(self.repl.onecmd("alias a"))
        self.assertEqual(self.repl.aliases, {})
        self.assertTrue(self.stdout.getvalue().startswith("invalid Command: "))
        self.assertTrue(self.stdout.getvalue().endswith("\n"))

    def test_import(self) -> None:
        """test importing aliases"""
        self.assertFalse(self.repl.onecmd(
            "import SUCC = lambda_calculus.terms.arithmetic.SUCCESSOR"
        ))
        self.assertEqual(
            self.repl.aliases,
            {
                "SUCC": SUCCESSOR
            }
        )

    def test_invalid_import(self) -> None:
        """test handling of invalid imports"""
        for location in (
            "lambda_calculus.terms.arithmetic.SUCCESSORX",
            "lambda_calculus.terms.arithmeticX.SUCCESSOR"
        ):
            self.assertFalse(self.repl.onecmd(f"import SUCC = {location}"))
            self.assertEqual(self.repl.aliases, {})
            self.assertTrue(self.stdout.getvalue().startswith("Error while importing: "))
            self.assertTrue(self.stdout.getvalue().endswith("\n"))
            self.stdout.seek(0)
            self.stdout.truncate(0)
        self.assertFalse(self.repl.onecmd("import SUCC = lambda_calculus.terms.arithmetic.number"))
        self.assertEqual(self.repl.aliases, {})
        self.assertTrue(self.stdout.getvalue().startswith("Error"))
        self.assertTrue(self.stdout.getvalue().endswith("\n"))

    def test_no_import_value(self) -> None:
        """test handling missing import values"""
        self.assertFalse(self.repl.onecmd("import a"))
        self.assertEqual(self.repl.aliases, {})
        self.assertTrue(self.stdout.getvalue().startswith("invalid Command: "))
        self.assertTrue(self.stdout.getvalue().endswith("\n"))

    def test_aliases(self) -> None:
        """test listing aliases"""
        self.assertFalse(self.repl.onecmd("alias x = 1"))
        self.assertFalse(self.repl.onecmd("alias a = x b"))
        self.assertFalse(self.repl.onecmd("alias b = b c"))
        self.assertFalse(self.repl.onecmd("aliases"))
        self.assertEqual(
            self.stdout.getvalue(),
            "x = 1\na = (1 b)\nb = (b c)\n"
        )

    def test_clear(self) -> None:
        """test clearing aliases"""
        self.assertFalse(self.repl.onecmd("alias x = 1"))
        self.assertFalse(self.repl.onecmd("alias a = x b"))
        self.assertFalse(self.repl.onecmd("alias b = b c"))
        self.assertFalse(self.repl.onecmd("clear x"))
        self.assertEqual(
            self.repl.aliases,
            {
                "a": Variable("1").apply_to(Variable("b")),
                "b": Variable("b").apply_to(Variable("c"))
            }
        )
        self.assertEqual(self.stdout.getvalue(), "")

    def test_clear_all(self) -> None:
        """test clearing all aliases"""
        self.assertFalse(self.repl.onecmd("alias x = 1"))
        self.assertFalse(self.repl.onecmd("alias a = x b"))
        self.assertFalse(self.repl.onecmd("alias b = b c"))
        self.assertFalse(self.repl.onecmd("clear"))
        self.assertEqual(self.repl.aliases, {})
        self.assertEqual(self.stdout.getvalue(), "")

    def test_exit(self) -> None:
        """test exiting the REPL"""
        self.assertTrue(self.repl.onecmd("exit"))
        self.assertTrue(self.stdout.getvalue().startswith("Exiting "))

    def test_eof(self) -> None:
        """test handling EOF"""
        self.assertTrue(self.repl.onecmd("EOF"))
        self.assertTrue(self.stdout.getvalue().startswith("Exiting "))
