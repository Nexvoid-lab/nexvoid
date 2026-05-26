# src/tokens.py
"""Token definitions for Nexvoid lexer"""


class Token:
    def __init__(self, type, value, line, col):
        self.type = type
        self.value = value
        self.line = line
        self.col = col
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, L{self.line}:C{self.col})"


class TokenType:
    # Keywords
    FUN = 'FUN'
    TASK = 'TASK'
    WAIT = 'WAIT'
    RETURN = 'RETURN'
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    REPEAT = 'REPEAT'
    AS = 'AS'
    COUT = 'COUT'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    PASS = 'PASS'
    IMPORT = 'IMPORT'
    FROM = 'FROM'
    ARRAY = 'ARRAY'
    MAP = 'MAP'
    CLASS = 'CLASS'
    PUBLIC = 'PUBLIC'
    PRIVATE = 'PRIVATE'
    AT = 'AT'
    COLON = 'COLON'
    IN = 'IN'
    PROTOCOL = 'PROTOCOL'
    IMPLEMENTS = 'IMPLEMENTS'
    INT = 'INT'
    TEXT = 'TEXT'
    BOOL = 'BOOL'
    FLOAT = 'FLOAT'
    VOID = 'VOID'
    
    
    # Literals
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    IDENT = 'IDENT'
    
    
    # Operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULT = 'MULT'
    DIV = 'DIV'
    MOD = 'MOD'
    FLOORDIV = 'FLOORDIV'
    POWER = 'POWER'
    ASSIGN = 'ASSIGN'
    EQ = 'EQ'
    NE = 'NE'
    LT = 'LT'
    GT = 'GT'
    LE = 'LE'
    GE = 'GE'
    DOT = 'DOT'
    WHERE = 'WHERE'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    
    # Delimiters
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    COMMA = 'COMMA'
    
    # Indentation
    INDENT = 'INDENT'
    DEDENT = 'DEDENT'
    
    #statement termination
    NEWLINE = 'NEWLINE'

    # Special
    EOF = 'EOF'