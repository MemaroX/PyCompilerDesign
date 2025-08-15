from compiler.lexer.token import Token, TokenType
from compiler.ast_nodes import Program, Statement, Expression, LiteralExpression, BinaryOperation, VariableDeclaration, AssignmentStatement, IdentifierExpression
from compiler.errors import SyntaxError

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []

    # Precedence levels for operators
    precedence = {
        TokenType.ASSIGN: 1,
        TokenType.LOGICAL_OR: 2,
        TokenType.LOGICAL_AND: 3,
        TokenType.BITWISE_OR: 4,
        TokenType.BITWISE_XOR: 5,
        TokenType.BITWISE_AND: 6,
        TokenType.EQUAL: 7,
        TokenType.NOT_EQUAL: 7,
        TokenType.LESS_THAN: 8,
        TokenType.GREATER_THAN: 8,
        TokenType.LESS_EQUAL: 8,
        TokenType.GREATER_EQUAL: 8,
        TokenType.LEFT_SHIFT: 9,
        TokenType.RIGHT_SHIFT: 9,
        TokenType.PLUS: 10,
        TokenType.MINUS: 10,
        TokenType.MULTIPLY: 11,
        TokenType.DIVIDE: 11,
        TokenType.MODULO: 11,
    }

    def _get_precedence(self, token_type: TokenType) -> int:
        return self.precedence.get(token_type, 0)

    def _current_token(self) -> Token:
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return Token(TokenType.EOF, "", -1, -1) # Return an EOF token

    def _peek_token(self, offset: int = 1) -> Token:
        peek_index = self.current_token_index + offset
        while peek_index < len(self.tokens) and self.tokens[peek_index].type == TokenType.NEWLINE:
            peek_index += 1
        if peek_index < len(self.tokens):
            return self.tokens[peek_index]
        return Token(TokenType.EOF, "", -1, -1)

    def _advance(self):
        self.current_token_index += 1

    def _eat(self, token_type: TokenType):
        if self._current_token().type == token_type:
            self._advance()
        else:
            token = self._current_token()
            raise SyntaxError(
                f"Expected token type {token_type.name}, but got {token.type.name}",
                line=token.line,
                column=token.column
            )

    def _synchronize(self):
        self._advance()
        while self._current_token().type != TokenType.EOF:
            if self._current_token().type == TokenType.SEMICOLON:
                self._advance()
                return
            # Synchronize to the next statement
            if self._current_token().type in [TokenType.INT, TokenType.CHAR_KW, TokenType.FLOAT_KW, TokenType.DOUBLE, TokenType.LET]:
                return
            self._advance()

    def parse(self) -> Program:
        return self.parse_program()

    def parse_program(self) -> Program:
        statements = []
        while self._current_token().type == TokenType.NEWLINE:
            self._advance()
        while self._current_token().type != TokenType.EOF:
            if self._current_token().type == TokenType.EOF:
                break
            try:
                statement = self.parse_statement()
                if statement:
                    statements.append(statement)
            except SyntaxError as e:
                self.errors.append(e)
                self._synchronize()
            while self._current_token().type == TokenType.NEWLINE:
                self._advance()
        return Program(statements)

    def parse_statement(self) -> Statement:
        # Check for typed variable declarations (e.g., int x = 10;)
        if self._current_token().type in [TokenType.INT, TokenType.CHAR_KW, TokenType.FLOAT_KW, TokenType.DOUBLE]: # Add other types as needed
            return self._parse_typed_variable_declaration()
        elif self._current_token().type == TokenType.LET:
            return self._parse_variable_declaration()
        elif self._current_token().type == TokenType.IDENTIFIER and self._peek_token().type == TokenType.ASSIGN:
            return self._parse_assignment_statement()
        else:
            # As a fallback, try to parse an expression statement.
            # This could be an expression followed by a semicolon.
            expression = self.parse_expression()
            if self._current_token().type == TokenType.SEMICOLON:
                self._eat(TokenType.SEMICOLON)
                return expression
            else:
                token = self._current_token()
                raise SyntaxError(
                    f"Unexpected token {token.type.name}. Expected a statement or expression.",
                    line=token.line,
                    column=token.column
                )

    def _parse_typed_variable_declaration(self) -> VariableDeclaration:
        type_token = self._current_token()
        self._advance() # Consume the type token (e.g., INT)
        identifier_token = self._current_token()
        self._eat(TokenType.IDENTIFIER)
        initializer = None
        if self._current_token().type == TokenType.ASSIGN:
            self._eat(TokenType.ASSIGN)
            initializer = self.parse_expression()
        self._eat(TokenType.SEMICOLON)
        return VariableDeclaration(identifier_token.value, type_token.value, initializer)

    def _parse_variable_declaration(self) -> VariableDeclaration:
        self._eat(TokenType.LET)
        identifier_token = self._current_token()
        self._eat(TokenType.IDENTIFIER)
        initializer = None
        if self._current_token().type == TokenType.ASSIGN:
            self._eat(TokenType.ASSIGN)
            initializer = self.parse_expression()
        self._eat(TokenType.SEMICOLON)
        return VariableDeclaration(identifier_token.value, None, initializer)

    def _parse_assignment_statement(self) -> AssignmentStatement:
        identifier_token = self._current_token()
        self._eat(TokenType.IDENTIFIER)
        self._eat(TokenType.ASSIGN)
        expression = self.parse_expression()
        self._eat(TokenType.SEMICOLON)
        return AssignmentStatement(identifier_token.value, expression)

    def parse_expression(self, precedence: int = 0) -> Expression:
        left = self._parse_primary_expression()

        while precedence < self._get_precedence(self._current_token().type):
            operator_token = self._current_token()
            self._eat(operator_token.type)
            right = self.parse_expression(self._get_precedence(operator_token.type))
            left = BinaryOperation(left, operator_token.value, right)
        return left

    def _parse_primary_expression(self) -> Expression:
        token = self._current_token()
        if token.type in [TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING, TokenType.CHAR, TokenType.BOOLEAN]:
            self._advance()
            return LiteralExpression(token.value)
        elif token.type == TokenType.IDENTIFIER:
            self._advance()
            return IdentifierExpression(token.value)
        elif token.type == TokenType.LPAREN:
            self._eat(TokenType.LPAREN)
            expression = self.parse_expression()
            self._eat(TokenType.RPAREN)
            return expression
        else:
            raise SyntaxError(
                f"Unexpected token {token.type.name} when parsing expression.",
                line=token.line,
                column=token.column
            )
