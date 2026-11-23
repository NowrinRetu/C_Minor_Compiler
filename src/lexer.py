
from tokens import Token, TokenKind
from diagnostics import LexerError


KEYWORDS = {
    "int": TokenKind.INT,
    "void": TokenKind.VOID,
    "if": TokenKind.IF,
    "else": TokenKind.ELSE,
    "while": TokenKind.WHILE,
    "for": TokenKind.FOR,
    "break": TokenKind.BREAK,
    "continue": TokenKind.CONTINUE,
    "return": TokenKind.RETURN,
}


OPERATORS = {
    "==": TokenKind.EQUAL,
    "!=": TokenKind.NOT_EQUAL,
    "<=": TokenKind.LESS_EQUAL,
    ">=": TokenKind.GREATER_EQUAL,
    "&&": TokenKind.AND,
    "||": TokenKind.OR,
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.MULTIPLY,
    "/": TokenKind.DIVIDE,
    "%": TokenKind.MODULO,
    "<": TokenKind.LESS,
    ">": TokenKind.GREATER,
    "!": TokenKind.NOT,
    "=": TokenKind.ASSIGN,
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
    "{": TokenKind.LBRACE,
    "}": TokenKind.RBRACE,
    ";": TokenKind.SEMICOLON,
    ",": TokenKind.COMMA,
}


class Lexer:

    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def current_char(self):
        if self.position >= len(self.source):
            return None

        return self.source[self.position]

    def peek(self, offset=1):
        index = self.position + offset

        if index >= len(self.source):
            return None

        return self.source[index]

    def advance(self):
        char = self.current_char()

        if char is None:
            return None

        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def add_token(self, kind, lexeme, line, column):
        token = Token(kind, lexeme, line, column)
        self.tokens.append(token)

    def skip_whitespace(self):
        while self.current_char() is not None:
            if self.current_char() in " \t\r\n":
                self.advance()
            else:
                break

    def skip_comment(self):

        # Single-line comment
        if (
            self.current_char() == "/"
            and self.peek() == "/"
        ):
            while (
                self.current_char() is not None
                and self.current_char() != "\n"
            ):
                self.advance()

            return True

        # Multi-line comment
        if (
            self.current_char() == "/"
            and self.peek() == "*"
        ):
            start_line = self.line
            start_column = self.column

            self.advance()
            self.advance()

            while self.current_char() is not None:

                if (
                    self.current_char() == "*"
                    and self.peek() == "/"
                ):
                    self.advance()
                    self.advance()
                    return True

                self.advance()

            raise LexerError(
                "Unterminated block comment",
                start_line,
                start_column
            )

        return False

    def scan_identifier(self):

        start_line = self.line
        start_column = self.column
        start_position = self.position

        while self.current_char() is not None:

            char = self.current_char()

            if (
                char.isascii()
                and (
                    char.isalpha()
                    or char.isdigit()
                    or char == "_"
                )
            ):
                self.advance()
            else:
                break

        lexeme = self.source[
            start_position:self.position
        ]

        if lexeme in KEYWORDS:
            kind = KEYWORDS[lexeme]
        else:
            kind = TokenKind.IDENTIFIER

        self.add_token(
            kind,
            lexeme,
            start_line,
            start_column
        )

    def scan_number(self):

        start_line = self.line
        start_column = self.column
        start_position = self.position

        while self.current_char() is not None:

            char = self.current_char()

            if char.isascii() and char.isdigit():
                self.advance()
            else:
                break

        lexeme = self.source[
            start_position:self.position
        ]

        value = int(lexeme)

        if value > 2147483647:
            raise LexerError(
                "Integer literal exceeds maximum allowed value",
                start_line,
                start_column
            )

        self.add_token(
            TokenKind.INTEGER,
            lexeme,
            start_line,
            start_column
        )

    def tokenize(self):

        while self.current_char() is not None:

            self.skip_whitespace()

            if self.current_char() is None:
                break

            if self.skip_comment():
                continue

            char = self.current_char()

            # Identifier or keyword
            if char.isascii() and (
                char.isalpha() or char == "_"
            ):
                self.scan_identifier()
                continue

            # Integer number
            if char.isascii() and char.isdigit():
                self.scan_number()
                continue

            start_line = self.line
            start_column = self.column

            # Longest-match operator checking
            two_chars = (
                char + (self.peek() or "")
            )

            if two_chars in OPERATORS:

                self.add_token(
                    OPERATORS[two_chars],
                    two_chars,
                    start_line,
                    start_column
                )

                self.advance()
                self.advance()
                continue

            # Single-character operator
            if char in OPERATORS:

                self.add_token(
                    OPERATORS[char],
                    char,
                    start_line,
                    start_column
                )

                self.advance()
                continue

            # Invalid character
            raise LexerError(
                f"Invalid character '{char}'",
                start_line,
                start_column
            )

        # End of file token
        self.add_token(
            TokenKind.EOF,
            "",
            self.line,
            self.column
        )

        return self.tokens
