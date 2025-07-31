import re
from typing import List, Optional
from .token import TokenType, Token

class CppLexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.symbol_table = {}
        
        # C++ keywords mapping
        self.keywords = {
            # C keywords
            'auto': TokenType.AUTO,
            'break': TokenType.BREAK,
            'case': TokenType.CASE,
            'char': TokenType.CHAR_KW,
            'const': TokenType.CONST,
            'continue': TokenType.CONTINUE,
            'default': TokenType.DEFAULT,
            'do': TokenType.DO,
            'double': TokenType.DOUBLE,
            'else': TokenType.ELSE,
            'enum': TokenType.ENUM,
            'extern': TokenType.EXTERN,
            'float': TokenType.FLOAT_KW,
            'for': TokenType.FOR,
            'goto': TokenType.GOTO,
            'if': TokenType.IF,
            'int': TokenType.INT,
            'long': TokenType.LONG,
            'register': TokenType.REGISTER,
            'return': TokenType.RETURN,
            'short': TokenType.SHORT,
            'signed': TokenType.SIGNED,
            'sizeof': TokenType.SIZEOF,
            'static': TokenType.STATIC,
            'struct': TokenType.STRUCT,
            'switch': TokenType.SWITCH,
            'typedef': TokenType.TYPEDEF,
            'union': TokenType.UNION,
            'unsigned': TokenType.UNSIGNED,
            'void': TokenType.VOID,
            'volatile': TokenType.VOLATILE,
            'while': TokenType.WHILE,
            
            # C++ keywords
            'class': TokenType.CLASS,
            'namespace': TokenType.NAMESPACE,
            'using': TokenType.USING,
            'public': TokenType.PUBLIC,
            'private': TokenType.PRIVATE,
            'protected': TokenType.PROTECTED,
            'virtual': TokenType.VIRTUAL,
            'override': TokenType.OVERRIDE,
            'final': TokenType.FINAL,
            'new': TokenType.NEW,
            'delete': TokenType.DELETE,
            'this': TokenType.THIS,
            'template': TokenType.TEMPLATE,
            'typename': TokenType.TYPENAME,
            'operator': TokenType.OPERATOR,
            'friend': TokenType.FRIEND,
            'inline': TokenType.INLINE,
            'explicit': TokenType.EXPLICIT,
            'mutable': TokenType.MUTABLE,
            'constexpr': TokenType.CONSTEXPR,
            'nullptr': TokenType.NULLPTR,
            'decltype': TokenType.DECLTYPE,
            'noexcept': TokenType.NOEXCEPT,
            'static_assert': TokenType.STATIC_ASSERT,
            'thread_local': TokenType.THREAD_LOCAL,
            'alignas': TokenType.ALIGNAS,
            'alignof': TokenType.ALIGNOF,
            'let': TokenType.LET,
            
            # Boolean literals
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN,
        }
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> None:
        if self.pos < len(self.source) and self.source[self.pos] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
    
    def skip_whitespace(self) -> None:
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def read_number(self) -> Token:
        start_pos = self.pos
        start_column = self.column
        is_float = False
        
        # Read integer part
        while self.current_char() and self.current_char().isdigit():
            self.advance()
        
        # Check for decimal point
        if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
            is_float = True
            self.advance()  # consume '.'
            while self.current_char() and self.current_char().isdigit():
                self.advance()
            
        # Check for scientific notation
        if self.current_char() and self.current_char().lower() == 'e':
            is_float = True
            self.advance() # consume 'e' or 'E'
            if self.current_char() and self.current_char() in '+-':
                self.advance()
            while self.current_char() and self.current_char().isdigit():
                self.advance()
            
        value_str = self.source[start_pos:self.pos]
        if is_float:
            return Token(TokenType.FLOAT, float(value_str), self.line, start_column)
        return Token(TokenType.INTEGER, int(value_str), self.line, start_column)
    
    def read_string(self, quote_char: str) -> Token:
        start_column = self.column
        value = ""
        self.advance()  # skip opening quote
        
        while True:
            current = self.current_char()
            if current is None:
                # Unterminated string literal
                break
            
            if current == quote_char:
                self.advance() # consume closing quote
                break

            if current == '\\':
                self.advance() # consume the backslash
                escaped_char = self.current_char()
                if escaped_char is None:
                    # Trailing backslash, treat as literal backslash
                    value += '\\'
                    break # End of source
                
                if escaped_char == 'n':
                    value += '\n'
                elif escaped_char == 't':
                    value += '\t'
                elif escaped_char == 'r':
                    value += '\r'
                elif escaped_char == '\\':
                    value += '\\'
                elif escaped_char == '"':
                    value += '"'
                elif escaped_char == "'":
                    value += "'"
                else:
                    # Unrecognized escape sequence, keep the character as is
                    value += escaped_char
                self.advance() # consume the escaped character
            else:
                value += current
                self.advance()

        token_type = TokenType.STRING if quote_char == '"' else TokenType.CHAR
        return Token(token_type, value, self.line, start_column)
    
    def read_identifier(self) -> Token:
        start_pos = self.pos
        start_column = self.column
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            self.advance()
        
        value = self.source[start_pos:self.pos]
        token_type = self.keywords.get(value, TokenType.IDENTIFIER)
        
        if token_type == TokenType.IDENTIFIER and value not in self.symbol_table:
            self.symbol_table[value] = {'line': self.line, 'column': start_column}
            
        return Token(token_type, value, self.line, start_column)
    
    def read_single_line_comment(self) -> Token:
        start_column = self.column
        start_pos = self.pos
        
        while self.current_char() and self.current_char() != '\n':
            self.advance()
        
        return Token(TokenType.SINGLE_LINE_COMMENT, 
                    self.source[start_pos:self.pos], self.line, start_column)
    
    def read_multi_line_comment(self) -> Token:
        start_column = self.column
        start_pos = self.pos
        
        self.advance()  # skip '/'
        self.advance()  # skip '*'
        
        while self.current_char():
            if self.current_char() == '*' and self.peek_char() == '/':
                self.advance()  # skip '*'
                self.advance()  # skip '/'
                break
            self.advance()
        
        return Token(TokenType.MULTI_LINE_COMMENT, 
                    self.source[start_pos:self.pos], self.line, start_column)
    
    def get_next_token(self) -> Token:
        # print(f"[DEBUG] get_next_token: current_char={self.current_char()!r}, pos={self.pos}, line={self.line}, column={self.column}")
        while self.current_char():
            # Handle whitespace
            if self.current_char() in ' \t\r':
                start_pos = self.pos
                start_column = self.column
                self.skip_whitespace()
                return Token(TokenType.WHITESPACE, self.source[start_pos:self.pos], self.line, start_column)
            
            # Newlines
            if self.current_char() == '\n':
                token = Token(TokenType.NEWLINE, '\n', self.line, self.column)
                self.advance()
                # print(f"[DEBUG] get_next_token: returning NEWLINE: {token}")
                return token
            
            # Comments (check before / operator)
            if self.current_char() == '/':
                if self.peek_char() == '/':
                    comment_token = self.read_single_line_comment()
                    # print(f"[DEBUG] get_next_token: returning SINGLE_LINE_COMMENT: {comment_token}")
                    return comment_token
                elif self.peek_char() == '*':
                    comment_token = self.read_multi_line_comment()
                    # print(f"[DEBUG] get_next_token: returning MULTI_LINE_COMMENT: {comment_token}")
                    return comment_token

            # Three-character operators (check before two-character)
            char = self.current_char()
            next_char = self.peek_char()
            third_char = self.peek_char(2)

            if char == '<' and next_char == '<' and third_char == '=':
                token = Token(TokenType.LEFT_SHIFT_ASSIGN, '<<=', self.line, self.column)
                self.advance()
                self.advance()
                self.advance()
                # print(f"[DEBUG] get_next_token: returning LEFT_SHIFT_ASSIGN: {token}")
                return token
            
            if char == '>' and next_char == '>' and third_char == '=':
                token = Token(TokenType.RIGHT_SHIFT_ASSIGN, '>>=', self.line, self.column)
                self.advance()
                self.advance()
                self.advance()
                return token

            # Two-character operators
            two_char_ops = {
                '++': TokenType.INCREMENT,
                '--': TokenType.DECREMENT,
                '+=': TokenType.PLUS_ASSIGN,
                '-=': TokenType.MINUS_ASSIGN,
                '*=': TokenType.MULTIPLY_ASSIGN,
                '%=': TokenType.MODULO_ASSIGN,
                '==': TokenType.EQUAL,
                '!=': TokenType.NOT_EQUAL,
                '<=': TokenType.LESS_EQUAL,
                '>=': TokenType.GREATER_EQUAL,
                '&&': TokenType.LOGICAL_AND,
                '||': TokenType.LOGICAL_OR,
                '<<': TokenType.LEFT_SHIFT,
                '>>': TokenType.RIGHT_SHIFT,
                '&=': TokenType.BITWISE_AND_ASSIGN,
                '|=': TokenType.BITWISE_OR_ASSIGN,
                '^=': TokenType.BITWISE_XOR_ASSIGN,
                '->': TokenType.ARROW,
                '::': TokenType.SCOPE_RESOLUTION,
                '/=': TokenType.DIVIDE_ASSIGN, # Moved here
            }
            
            two_char = char + (next_char or '')
            if two_char in two_char_ops:
                token = Token(two_char_ops[two_char], two_char, self.line, self.column)
                self.advance()
                self.advance()
                # print(f"[DEBUG] get_next_token: returning TWO_CHAR_OP: {token}")
                return token
            
            # Numbers
            if self.current_char() and self.current_char().isdigit():
                num_token = self.read_number()
                return Token(TokenType.LITERAL, num_token.value, num_token.line, num_token.column)
            
            # Identifiers and keywords
            if self.current_char() and (self.current_char().isalpha() or self.current_char() == '_'):
                id_token = self.read_identifier()
                return id_token
            
            # String literals
            if self.current_char() == '"':
                str_token = self.read_string('"')
                return Token(TokenType.LITERAL, str_token.value, str_token.line, str_token.column)
            
            # Character literals
            if self.current_char() == "'":
                char_token = self.read_string("'")
                return Token(TokenType.LITERAL, char_token.value, char_token.line, char_token.column)

            # Single-character operators and punctuation
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE, 
                '%': TokenType.MODULO,
                '=': TokenType.ASSIGN,
                '<': TokenType.LESS_THAN,
                '>': TokenType.GREATER_THAN,
                '!': TokenType.LOGICAL_NOT,
                '&': TokenType.BITWISE_AND,
                '|': TokenType.BITWISE_OR,
                '^': TokenType.BITWISE_XOR,
                '~': TokenType.BITWISE_NOT,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
                '?': TokenType.QUESTION,
                ':': TokenType.COLON,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                '#': TokenType.HASH,
            }
            
            if char in single_char_tokens:
                token = Token(single_char_tokens[char], char, self.line, self.column)
                self.advance()
                # print(f"[DEBUG] get_next_token: returning SINGLE_CHAR_OP/PUNCTUATION: {token}")
                return token
            
            # Unknown character
            token = Token(TokenType.UNKNOWN, char, self.line, self.column)
            self.advance()
            # print(f"[DEBUG] get_next_token: returning UNKNOWN: {token}")
            return token
        
        # print(f"[DEBUG] get_next_token: returning EOF")
        return Token(TokenType.EOF, '', self.line, self.column)
    
    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens
    
    def tokenize_and_filter(self, include_comments: bool = False, 
                           include_newlines: bool = False) -> tuple[List[Token], dict]:
        """Tokenize and optionally filter out comments and newlines"""
        tokens = self.tokenize()
        
        if not include_comments:
            tokens = [t for t in tokens if t.type not in 
                     (TokenType.SINGLE_LINE_COMMENT, TokenType.MULTI_LINE_COMMENT)]
        
        if not include_newlines:
            tokens = [t for t in tokens if t.type != TokenType.NEWLINE]
        
        return tokens, self.symbol_table