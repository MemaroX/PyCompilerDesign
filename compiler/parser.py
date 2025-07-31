from compiler.lexer.token import Token, TokenType
from compiler.ast_nodes import Program, Statement, Expression, LiteralExpression, BinaryOperation, VariableDeclaration, AssignmentStatement, IdentifierExpression

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current_token_index = 0

    # Define a set of binary operator token types
    binary_operators = {
        TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
        TokenType.MODULO, TokenType.ASSIGN, TokenType.EQUAL, TokenType.NOT_EQUAL,
        TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_EQUAL,
        TokenType.GREATER_EQUAL, TokenType.LOGICAL_AND, TokenType.LOGICAL_OR,
        TokenType.BITWISE_AND, TokenType.BITWISE_OR, TokenType.BITWISE_XOR,
        TokenType.LEFT_SHIFT, TokenType.RIGHT_SHIFT
    }

    def _current_token(self) -> Token:
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return Token(TokenType.EOF, "", -1, -1) # Return an EOF token

    def _peek_token(self, offset: int = 1) -> Token:
        peek_index = self.current_token_index + offset
        while peek_index < len(self.tokens) and self.tokens[peek_index].type == TokenType.WHITESPACE:
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
        # Check for typed variable declarations (e.g., int x = 10;)
        if self._current_token().type in [TokenType.INT, TokenType.CHAR_KW, TokenType.FLOAT_KW, TokenType.DOUBLE]: # Add other types as needed
            return self._parse_typed_variable_declaration()
        elif self._current_token().type == TokenType.LET:
            return self._parse_variable_declaration()
        elif self._current_token().type == TokenType.IDENTIFIER and self._peek_token().type == TokenType.ASSIGN:
            return self._parse_assignment_statement()
        else:
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

    def _parse_typed_variable_declaration(self) -> VariableDeclaration:
        type_token = self._current_token()
        self._advance() # Consume the type token (e.g., INT)
        self._skip_whitespace()
        identifier_token = self._current_token()
        self._eat(TokenType.IDENTIFIER)
        initializer = None
        self._skip_whitespace()
        if self._current_token().type == TokenType.ASSIGN:
            self._eat(TokenType.ASSIGN)
            self._skip_whitespace()
            initializer = self.parse_expression()
        self._eat(TokenType.SEMICOLON)
        return VariableDeclaration(identifier_token.value, type_token.value, initializer)

    def _parse_variable_declaration(self) -> VariableDeclaration:
        self._eat(TokenType.LET)
        self._skip_whitespace()
        identifier_token = self._current_token()
        self._eat(TokenType.IDENTIFIER)
        initializer = None
        self._skip_whitespace()
        if self._current_token().type == TokenType.ASSIGN:
            self._eat(TokenType.ASSIGN)
            self._skip_whitespace()
            initializer = self.parse_expression()
        self._eat(TokenType.SEMICOLON)
        return VariableDeclaration(identifier_token.value, initializer)

    def _parse_assignment_statement(self) -> AssignmentStatement:
        identifier_token = self._current_token()
        self._eat(TokenType.IDENTIFIER)
        self._skip_whitespace()
        self._eat(TokenType.ASSIGN)
        self._skip_whitespace()
        expression = self.parse_expression()
        self._eat(TokenType.SEMICOLON)
        return AssignmentStatement(identifier_token.value, expression)

    def parse_expression(self) -> Expression:
        self._skip_whitespace()
        left = self._parse_primary_expression()

        self._skip_whitespace()

        while self._current_token().type in self.binary_operators:
            operator_token = self._current_token()
            self._eat(operator_token.type)
            self._skip_whitespace()
            right = self._parse_primary_expression()
            left = BinaryOperation(left, operator_token.value, right)
            self._skip_whitespace()
        return left

    def _parse_primary_expression(self) -> Expression:
        self._skip_whitespace()
        if self._current_token().type == TokenType.LITERAL:
            value = self._current_token().value
            self._eat(TokenType.LITERAL)
            return LiteralExpression(value)
        elif self._current_token().type == TokenType.IDENTIFIER:
            value = self._current_token().value
            self._eat(TokenType.IDENTIFIER)
            return IdentifierExpression(value)
        else:
            raise ValueError(
                f"Expected LITERAL or IDENTIFIER, "
                f"but got {self._current_token().type.name} "
                f"at line {self._current_token().line}, column {self._current_token().column}"
            )