from typing import NamedTuple, List, Optional
import re
from enum import Enum

class TokenType(Enum):
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    OPERATOR = "OPERATOR"
    LITERAL = "LITERAL"
    STRING = "STRING"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    WHITESPACE = "WHITESPACE"
    NEWLINE = "NEWLINE"
    EOF = "EOF" # End of File

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.tokens: List[Token] = []
        self.current_pos = 0
        self.current_line = 1
        self.current_column = 1

        # Order matters here: more specific regexes should come before general ones
        self.token_patterns = [
            (TokenType.KEYWORD, r'\b(if|else|while|for|return)\b'),
            (TokenType.OPERATOR, r'[+\-*/=<>!]+'),
            (TokenType.LITERAL, r'\d+'),
            (TokenType.STRING, r'".*?"'),
            (TokenType.LPAREN, r'\('),
            (TokenType.RPAREN, r'\)'),
            (TokenType.LBRACE, r'{'),
            (TokenType.RBRACE, r'}'),
            (TokenType.SEMICOLON, r';'),
            (TokenType.COMMA, r','),
            (TokenType.IDENTIFIER, r'[a-zA-Z_][a-zA-Z0-9_]*'), # Should be after keywords
            (TokenType.WHITESPACE, r'[ \t]+'),
            (TokenType.NEWLINE, r'\n'),
        ]

    def tokenize(self) -> List[Token]:
        while self.current_pos < len(self.code):
            token = self._get_next_token()
            if token and token.type not in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                self.tokens.append(token)
        self.tokens.append(Token(TokenType.EOF, "", self.current_line, self.current_column))
        return self.tokens

    def _get_next_token(self) -> Optional[Token]:
        for token_type, pattern in self.token_patterns:
            match = re.match(pattern, self.code[self.current_pos:])
            if match:
                value = match.group(0)
                token = Token(token_type, value, self.current_line, self.current_column)
                self._advance(len(value), token_type == TokenType.NEWLINE)
                return token
        
        # If no match, it's an invalid character
        raise ValueError(
            f"Invalid token at line {self.current_line}, column {self.current_column}: "
            f"'{self.code[self.current_pos]}'"
        )

    def _advance(self, length: int, is_newline: bool = False):
        self.current_pos += length
        if is_newline:
            self.current_line += 1
            self.current_column = 1
        else:
            self.current_column += length

    def peek(self, offset: int = 0) -> Optional[Token]:
        """Peeks at a token without consuming it."""
        if self.current_pos + offset >= len(self.tokens):
            return Token(TokenType.EOF, "", self.current_line, self.current_column) # Return EOF token
        return self.tokens[self.current_pos + offset]

    def consume(self) -> Optional[Token]:
        """Consumes the next token and returns it."""
        if self.current_pos >= len(self.tokens):
            return Token(TokenType.EOF, "", self.current_line, self.current_column) # Return EOF token
        token = self.tokens[self.current_pos]
        self.current_pos += 1
        return token