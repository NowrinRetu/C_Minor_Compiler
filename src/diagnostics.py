
class CompilerError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

        super().__init__(
            f"Error at line {line}, column {column}: {message}"
        )


class LexerError(CompilerError):
    pass


class ParserError(CompilerError):
    pass


class SemanticError(CompilerError):
    pass
