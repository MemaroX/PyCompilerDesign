class CompilerError(Exception):
    """Base class for all compiler errors."""
    pass

class SyntaxError(CompilerError):
    """Raised when a syntax error is found in the source code."""
    def __init__(self, message, line=None, column=None):
        super().__init__(message)
        self.line = line
        self.column = column

    def __str__(self):
        if self.line is not None and self.column is not None:
            return f"SyntaxError at line {self.line}, column {self.column}: {self.args[0]}"
        return f"SyntaxError: {self.args[0]}"
