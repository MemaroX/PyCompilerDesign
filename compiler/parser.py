from compiler.lexer.token import Token, TokenType
from compiler.ast_nodes import Program, Statement, Expression, LiteralExpression, BinaryOperation, VariableDeclaration, AssignmentStatement

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
        if self._current_token().type == TokenType.LET:
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

        while self._current_token().type == TokenType.OPERATOR:
            operator = self._current_token().value
            self._eat(TokenType.OPERATOR)
            self._skip_whitespace()
            right = self._parse_primary_expression()
            left = BinaryOperation(left, operator, right)
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
            return LiteralExpression(value) # For now, treat identifiers as literals in expressions
        else:
            raise ValueError(
                f"Expected LITERAL or IDENTIFIER, "
                f"but got {self._current_token().type.name} "
                f"at line {self._current_token().line}, column {self._current_token().column}"
            )