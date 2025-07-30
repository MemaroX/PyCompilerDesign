import unittest
from compiler.lexer import Lexer, Token
from compiler.parser import Parser
from compiler.ast_nodes import Program, Statement, Expression, LiteralExpression, BinaryOperation

class TestParser(unittest.TestCase):
    def test_parser_initialization(self):
        lexer = Lexer("1 + 2;")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        self.assertIsNotNone(parser)

    def test_parse_empty_program(self):
        lexer = Lexer("")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.assertIsInstance(program, Program)
        self.assertEqual(len(program.statements), 0)

    def test_parse_simple_program(self):
        # This test will be expanded as parsing logic is implemented
        lexer = Lexer("1 + 2;")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.assertIsInstance(program, Program)
        self.assertEqual(len(program.statements), 1)
        statement = program.statements[0]
        self.assertIsInstance(statement, BinaryOperation)
        self.assertIsInstance(statement.left, LiteralExpression)
        self.assertEqual(statement.left.value, "1")
        self.assertEqual(statement.operator, "+")
        self.assertIsInstance(statement.right, LiteralExpression)
        self.assertEqual(statement.right.value, "2")
