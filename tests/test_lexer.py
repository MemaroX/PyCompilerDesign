import unittest
from compiler.lexer import Lexer, Token

class TestLexer(unittest.TestCase):

    def test_lexer(self):
        code = 'if (x > 0) { return 1; }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        expected_tokens = [
            Token(type='KEYWORD', value='if', line=1, column=1),
            Token(type='WHITESPACE', value=' ', line=1, column=3),
            Token(type='LPAREN', value='(', line=1, column=4),
            Token(type='IDENTIFIER', value='x', line=1, column=5),
            Token(type='WHITESPACE', value=' ', line=1, column=6),
            Token(type='OPERATOR', value='>', line=1, column=7),
            Token(type='WHITESPACE', value=' ', line=1, column=8),
            Token(type='LITERAL', value='0', line=1, column=9),
            Token(type='RPAREN', value=')', line=1, column=10),
            Token(type='WHITESPACE', value=' ', line=1, column=11),
            Token(type='LBRACE', value='{', line=1, column=12),
            Token(type='WHITESPACE', value=' ', line=1, column=13),
            Token(type='KEYWORD', value='return', line=1, column=14),
            Token(type='WHITESPACE', value=' ', line=1, column=20),
            Token(type='LITERAL', value='1', line=1, column=21),
            Token(type='SEMICOLON', value=';', line=1, column=22),
            Token(type='WHITESPACE', value=' ', line=1, column=23),
            Token(type='RBRACE', value='}', line=1, column=24),
        ]

        self.assertEqual(tokens, expected_tokens)

if __name__ == '__main__':
    unittest.main()