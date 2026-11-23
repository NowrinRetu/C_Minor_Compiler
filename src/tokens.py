
from dataclasses import dataclass
from enum import Enum, auto


class TokenKind(Enum):
    # Special tokens
    EOF = auto()
    IDENTIFIER = auto()
    INTEGER = auto()

    # Keywords
    INT = auto()
    VOID = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()

    # Arithmetic operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()

    # Comparison operators
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()

    # Logical operators
    NOT = auto()
    AND = auto()
    OR = auto()

    # Assignment operator
    ASSIGN = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COMMA = auto()


@dataclass
class Token:
    kind: TokenKind
    lexeme: str
    line: int
    column: int
