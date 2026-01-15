"""
Custom exceptions for Zenith Analyser.
"""

class ZenithError(Exception):
    """Base exception for all Zenith Analyser errors."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    
    def __str__(self) -> str:
        return f"ZenithError: {self.message}"


class ZenithLexerError(ZenithError):
    """Exception raised during lexical analysis."""
    
    def __init__(self, message: str, line: int = None, column: int = None):
        self.line = line
        self.column = column
        if line is not None and column is not None:
            message = f"Lexing error at line {line}, column {column}: {message}"
        super().__init__(message)


class ZenithParserError(ZenithError):
    """Exception raised during parsing."""
    
    def __init__(self, message: str, token: dict = None):
        self.token = token
        if token:
            line = token.get('line', '?')
            col = token.get('col', '?')
            value = token.get('value', '')
            message = f"Parsing error at line {line}, column {col} (token: '{value}'): {message}"
        super().__init__(message)


class ZenithAnalyserError(ZenithError):
    """Exception raised during analysis."""
    
    def __init__(self, message: str, law_name: str = None, target_name: str = None):
        self.law_name = law_name
        self.target_name = target_name
        if law_name:
            message = f"Analysis error for law '{law_name}': {message}"
        elif target_name:
            message = f"Analysis error for target '{target_name}': {message}"
        super().__init__(message)


class ZenithValidationError(ZenithError):
    """Exception raised during validation."""
    
    def __init__(self, message: str, validation_type: str = None):
        self.validation_type = validation_type
        if validation_type:
            message = f"Validation error ({validation_type}): {message}"
        super().__init__(message)


class ZenithConfigurationError(ZenithError):
    """Exception raised for configuration errors."""
    pass


class ZenithRuntimeError(ZenithError):
    """Exception raised for runtime errors."""
    pass


class ZenithLimitError(ZenithError):
    """Exception raised when limits are exceeded."""
    
    def __init__(self, limit_type: str, limit_value: int, actual_value: int):
        message = f"{limit_type} limit exceeded: limit={limit_value}, actual={actual_value}"
        self.limit_type = limit_type
        self.limit_value = limit_value
        self.actual_value = actual_value
        super().__init__(message)


class ZenithTimeError(ZenithError):
    """Exception raised for time-related errors."""
    
    def __init__(self, message: str, time_value: str = None):
        self.time_value = time_value
        if time_value:
            message = f"Time error for value '{time_value}': {message}"
        super().__init__(message)
