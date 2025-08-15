import unittest
from compiler.lexer.lexer import CppLexer as Lexer
from compiler.parser import Parser
from compiler.ast_nodes import Program, BinaryOperation, LiteralExpression

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
        self.assertEqual(len(parser.errors), 0)

    def test_parse_simple_program(self):
        # This test will be expanded as parsing logic is implemented
        lexer = Lexer("1 + 2;")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.assertIsInstance(program, Program)
        self.assertEqual(len(program.statements), 1)
        self.assertEqual(len(parser.errors), 0)
        statement = program.statements[0]
        self.assertIsInstance(statement, BinaryOperation)
        self.assertIsInstance(statement.left, LiteralExpression)
        self.assertEqual(statement.left.value, "1")
        self.assertEqual(statement.operator, "+")
        self.assertIsInstance(statement.right, LiteralExpression)
        self.assertEqual(statement.right.value, "2")

    def test_invalid_statement(self):
        lexer = Lexer("let x = 5 y;")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.assertEqual(len(program.statements), 0)
        self.assertEqual(len(parser.errors), 1)
        self.assertIn("Expected token type SEMICOLON, but got IDENTIFIER", str(parser.errors[0]))

    def test_error_recovery(self):
        lexer = Lexer("let x = 5 y; let z = 10;")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.assertEqual(len(program.statements), 1)
        self.assertEqual(len(parser.errors), 1)
        self.assertIn("Expected token type SEMICOLON, but got IDENTIFIER", str(parser.errors[0]))
        # Check that the second statement was parsed correctly
        statement = program.statements[0]
        self.assertEqual(statement.identifier, 'z')
        self.assertEqual(statement.initializer.value, '10')

    def test_operator_precedence(self):
        lexer = Lexer("2 + 3 * 4;")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), 1)
        statement = program.statements[0]
        self.assertIsInstance(statement, BinaryOperation)
        self.assertEqual(statement.operator, "+")
        self.assertIsInstance(statement.left, LiteralExpression)
        self.assertEqual(statement.left.value, "2")
        right_node = statement.right
        self.assertIsInstance(right_node, BinaryOperation)
        self.assertEqual(right_node.operator, "*")
        self.assertEqual(right_node.left.value, "3")
        self.assertEqual(right_node.right.value, "4")

    def test_operator_associativity(self):
        lexer = Lexer("8 - 4 - 2;")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), 1)
        statement = program.statements[0]
        self.assertIsInstance(statement, BinaryOperation)
        self.assertEqual(statement.operator, "-")
        self.assertIsInstance(statement.right, LiteralExpression)
        self.assertEqual(statement.right.value, "2")
        left_node = statement.left
        self.assertIsInstance(left_node, BinaryOperation)
        self.assertEqual(left_node.operator, "-")
        self.assertEqual(left_node.left.value, "8")
        self.assertEqual(left_node.right.value, "4")

    def test_parenthesized_expressions(self):
        lexer = Lexer("(2 + 3) * 4;")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), 1)
        statement = program.statements[0]
        self.assertIsInstance(statement, BinaryOperation)
        self.assertEqual(statement.operator, "*")
        self.assertIsInstance(statement.right, LiteralExpression)
        self.assertEqual(statement.right.value, "4")
        left_node = statement.left
        self.assertIsInstance(left_node, BinaryOperation)
        self.assertEqual(left_node.operator, "+")
        self.assertEqual(left_node.left.value, "2")
        self.assertEqual(left_node.right.value, "3")
