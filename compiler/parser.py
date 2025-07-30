from compiler.lexer import Token, TokenType
from compiler.ast_nodes import Program, Statement, Expression, LiteralExpression, BinaryOperation

class Parser:
    def __init__(self, tokens: list[Token]):
        # The lexer should now handle token consumption and peeking
        # We'll pass the list of tokens to the parser, but the parser
        # will conceptually operate on a stream provided by the lexer.
        # For now, we'll simulate this by keeping the tokens list and an index.
        # In a more integrated system, the parser might directly receive a lexer instance.
        self.tokens = tokens
        self.current_token_index = 0

    def _current_token(self) -> Token:
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return Token(TokenType.EOF, "", -1, -1) # Return an EOF token

    def _advance(self):
        self.current_token_index += 1

    def _eat(self, token_type: TokenType):
        if self._current_token().type == token_type:
            self._advance()
        else:
            raise ValueError(
                f"Expected token type {token_type.name}, "
                f"but got {self._current_token().type.name} "
                f"at line {self._current_token().line}, column {self._current_token().column}"
            )

    def _skip_whitespace(self):
        while self._current_token().type in [TokenType.NEWLINE, TokenType.WHITESPACE]:
            self._advance()

    def parse(self) -> Program:
        return self.parse_program()

    def parse_program(self) -> Program:
        statements = []
        while self._current_token().type != TokenType.EOF:
            self._skip_whitespace()
            if self._current_token().type == TokenType.EOF:
                break
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
        return Program(statements)

    def parse_statement(self) -> Statement:
        expression = self.parse_expression()
        self._skip_whitespace()
        if self._current_token().type == TokenType.SEMICOLON:
            self._eat(TokenType.SEMICOLON)
            return expression
        else:
            raise ValueError(
                f"Expected SEMICOLON after expression, "
                f"but got {self._current_token().type.name} "
                f"at line {self._current_token().line}, column {self._current_token().column}"
            )

    def parse_expression(self) -> Expression:
        left = self._parse_primary_expression()

        self._skip_whitespace()

        while self._current_token().type == TokenType.OPERATOR:
            operator = self._current_token().value
            self._eat(TokenType.OPERATOR)
            self._skip_whitespace()
            right = self._parse_primary_expression()
            left = BinaryOperation(left, operator, right)
            self._skip_whitespace()
        return left

    def _parse_primary_expression(self) -> Expression:
        if self._current_token().type == TokenType.LITERAL:
            value = self._current_token().value
            self._eat(TokenType.LITERAL)
            return LiteralExpression(value)
        else:
            raise ValueError(
                f"Expected LITERAL, "
                f"but got {self._current_token().type.name} "
                f"at line {self._current_token().line}, column {self._current_token().column}"
            )