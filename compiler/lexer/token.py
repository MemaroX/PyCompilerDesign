from enum import Enum
from typing import NamedTuple

class TokenType(Enum):
    # Literals
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    CHAR = "CHAR"
    BOOLEAN = "BOOLEAN"
    
    # Identifiers
    IDENTIFIER = "IDENTIFIER"
    
    # Keywords
    AUTO = "auto"
    BREAK = "break"
    CASE = "case"
    CHAR_KW = "char"
    CONST = "const"
    CONTINUE = "continue"
    DEFAULT = "default"
    DO = "do"
    DOUBLE = "double"
    ELSE = "else"
    ENUM = "enum"
    EXTERN = "extern"
    FLOAT_KW = "float"
    FOR = "for"
    GOTO = "goto"
    IF = "if"
    INT = "int"
    LONG = "long"
    REGISTER = "register"
    RETURN = "return"
    SHORT = "short"
    SIGNED = "signed"
    SIZEOF = "sizeof"
    STATIC = "static"
    STRUCT = "struct"
    SWITCH = "switch"
    TYPEDEF = "typedef"
    UNION = "union"
    UNSIGNED = "unsigned"
    VOID = "void"
    VOLATILE = "volatile"
    WHILE = "while"
    LET = "let"
    
    # C++ specific keywords
    CLASS = "class"
    NAMESPACE = "namespace"
    USING = "using"
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    VIRTUAL = "virtual"
    OVERRIDE = "override"
    FINAL = "final"
    NEW = "new"
    DELETE = "delete"
    THIS = "this"
    TEMPLATE = "template"
    TYPENAME = "typename"
    OPERATOR = "operator"
    FRIEND = "friend"
    INLINE = "inline"
    EXPLICIT = "explicit"
    MUTABLE = "mutable"
    CONSTEXPR = "constexpr"
    NULLPTR = "nullptr"
    DECLTYPE = "decltype"
    NOEXCEPT = "noexcept"
    STATIC_ASSERT = "static_assert"
    THREAD_LOCAL = "thread_local"
    ALIGNAS = "alignas"
    ALIGNOF = "alignof"
    
    # Operators
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    ASSIGN = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="
    MULTIPLY_ASSIGN = "*="
    DIVIDE_ASSIGN = "/="
    MODULO_ASSIGN = "%="
    INCREMENT = "++"
    DECREMENT = "--"
    
    # Comparison operators
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    
    # Logical operators
    LOGICAL_AND = "&&"
    LOGICAL_OR = "||"
    LOGICAL_NOT = "!"
    
    # Bitwise operators
    BITWISE_AND = "&"
    BITWISE_OR = "|"
    BITWISE_XOR = "^"
    BITWISE_NOT = "~"
    LEFT_SHIFT = "<<"
    RIGHT_SHIFT = ">>"
    BITWISE_AND_ASSIGN = "&="
    BITWISE_OR_ASSIGN = "|="
    BITWISE_XOR_ASSIGN = "^="
    LEFT_SHIFT_ASSIGN = "<<="
    RIGHT_SHIFT_ASSIGN = ">>="
    
    # Punctuation
    SEMICOLON = ";"
    COMMA = ","
    DOT = "."
    ARROW = "->"
    SCOPE_RESOLUTION = "::"
    QUESTION = "?"
    COLON = ":"
    
    # Brackets and braces
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    
    # Preprocessor
    HASH = "#"
    
    # Comments
    SINGLE_LINE_COMMENT = "SINGLE_LINE_COMMENT"
    MULTI_LINE_COMMENT = "MULTI_LINE_COMMENT"
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int