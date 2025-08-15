import pytest
from compiler.lexer.lexer import CppLexer
from compiler.lexer.token import TokenType, Token

def test_empty_code():
    lexer = CppLexer("")
    tokens = lexer.tokenize()
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF

def test_whitespace_and_newline():
    lexer = CppLexer("   \n\t\r")
    tokens = lexer.tokenize_and_filter(include_newlines=True)
    # Expecting one NEWLINE token for '\n' and then EOF. '\t\r' are whitespace.
    assert len(tokens) == 2 
    assert tokens[0].type == TokenType.NEWLINE
    assert tokens[1].type == TokenType.EOF

def test_keywords():
    code = "int main class return"
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter()
    expected_types = [TokenType.INT, TokenType.IDENTIFIER, TokenType.CLASS, TokenType.RETURN, TokenType.EOF]
    assert [t.type for t in tokens] == expected_types
    assert [t.value for t in tokens[:-1]] == ["int", "main", "class", "return"]

def test_identifiers():
    code = "myVar _another_var ClassName123"
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter()
    expected_types = [TokenType.IDENTIFIER, TokenType.IDENTIFIER, TokenType.IDENTIFIER, TokenType.EOF]
    assert [t.type for t in tokens] == expected_types
    assert [t.value for t in tokens[:-1]] == ["myVar", "_another_var", "ClassName123"]

def test_integers():
    code = "123 0 456789"
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter()
    expected_types = [TokenType.INTEGER, TokenType.INTEGER, TokenType.INTEGER, TokenType.EOF]
    assert [t.type for t in tokens] == expected_types
    assert [t.value for t in tokens[:-1]] == ["123", "0", "456789"]

def test_floats():
    code = "1.0 3.14 0.5 1e5 1.2e-3"
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter()
    expected_types = [TokenType.FLOAT, TokenType.FLOAT, TokenType.FLOAT, TokenType.FLOAT, TokenType.FLOAT, TokenType.EOF]
    assert [t.type for t in tokens] == expected_types
    assert [t.value for t in tokens[:-1]] == ["1.0", "3.14", "0.5", "1e5", "1.2e-3"]

def test_strings():
    # Corrected test case for embedded escaped double quote
    code = '"hello world" "This is a \"quoted\" string"'
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter()
    expected_types = [TokenType.STRING, TokenType.STRING, TokenType.EOF]
    assert [t.type for t in tokens] == expected_types
    assert [t.value for t in tokens[:-1]] == ["hello world", 'This is a "quoted" string']

def test_chars():
    code = "'a' '\n' '\''"
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter()
    expected_types = [TokenType.CHAR, TokenType.CHAR, TokenType.CHAR, TokenType.EOF]
    assert [t.type for t in tokens] == expected_types
    assert [t.value for t in tokens[:-1]] == ["a", "\n", "'"]

def test_operators():
    code = "+ - * / = == != <= >= && || ! & | ^ ~ << >> += -= *= /= %= &= |= ^= <<= >>="
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter()
    expected_types = [
        TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.ASSIGN,
        TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
        TokenType.LOGICAL_AND, TokenType.LOGICAL_OR, TokenType.LOGICAL_NOT,
        TokenType.BITWISE_AND, TokenType.BITWISE_OR, TokenType.BITWISE_XOR, TokenType.BITWISE_NOT,
        TokenType.LEFT_SHIFT, TokenType.RIGHT_SHIFT,
        TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, TokenType.MULTIPLY_ASSIGN, TokenType.DIVIDE_ASSIGN, TokenType.MODULO_ASSIGN,
        TokenType.BITWISE_AND_ASSIGN, TokenType.BITWISE_OR_ASSIGN, TokenType.BITWISE_XOR_ASSIGN,
        TokenType.LEFT_SHIFT_ASSIGN, TokenType.RIGHT_SHIFT_ASSIGN,
        TokenType.EOF
    ]
    assert [t.type for t in tokens] == expected_types

def test_punctuation():
    code = "; , . -> :: ? : ( ) { } [ ] #"
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter()
    expected_types = [
        TokenType.SEMICOLON, TokenType.COMMA, TokenType.DOT, TokenType.ARROW, TokenType.SCOPE_RESOLUTION,
        TokenType.QUESTION, TokenType.COLON, TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE,
        TokenType.RBRACE, TokenType.LBRACKET, TokenType.RBRACKET, TokenType.HASH, TokenType.EOF
    ]
    assert [t.type for t in tokens] == expected_types

def test_single_line_comment():
    code = "// This is a comment\nint x;"
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter(include_comments=True, include_newlines=True)
    assert tokens[0].type == TokenType.SINGLE_LINE_COMMENT
    assert tokens[1].type == TokenType.NEWLINE
    assert tokens[2].type == TokenType.INT

def test_multi_line_comment():
    code = "/* This is a\nmulti-line comment */ int y;"
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter(include_comments=True)
    assert tokens[0].type == TokenType.MULTI_LINE_COMMENT
    assert tokens[1].type == TokenType.INT

def test_complex_code_snippet():
    code = '''\
    #include <iostream>
    int main() {
        // A simple program
        int x = 10;
        /* Another
         * comment */
        if (x > 5) {
            std::cout << "x is greater than 5" << std::endl;
        }
        return 0;
    } 
    '''
    lexer = CppLexer(code)
    tokens = lexer.tokenize_and_filter(include_comments=True, include_newlines=True)
    # Just check if it tokenizes without errors and has a reasonable number of tokens
    assert len(tokens) > 20
    assert tokens[-1].type == TokenType.EOF
