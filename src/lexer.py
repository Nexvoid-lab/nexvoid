# src/lexer.py
"""Lexer for Nexvoid - converts source code to tokens"""

from tokens import Token, TokenType


class NexvoidLexer:
    KEYWORDS = {
        'fun', 'task', 'wait', 'return',
        'if', 'else',
        'while', 'repeat', 'as',
        
        'true', 'false',
        'and', 'or', 'not','pass',
        'import', 'from',
        'array', 'map', 'class',
        'public', 'private', 'where', 'in', 
        'protocol', 'implements',
        
    }
    
    OPERATORS = {
        '==': TokenType.EQ,
        '!=': TokenType.NE,
        '<=': TokenType.LE,
        '>=': TokenType.GE,
        '//': TokenType.FLOORDIV,
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULT,
        '/': TokenType.DIV,
        '%': TokenType.MOD,
        '=': TokenType.ASSIGN,
        '<': TokenType.LT,
        '>': TokenType.GT,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        ',': TokenType.COMMA,
        '.': TokenType.DOT,
        '**': TokenType.POWER,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        '@': TokenType.AT,
        ':': TokenType.COLON,
        
    }
    
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.indent_stack = [0]
        self.pending_dedents = 0
    
    def error(self, msg):
        raise SyntaxError(f"Lexer Error at L{self.line}:C{self.col} - {msg}")
    
    def peek(self, offset=0):
        """Look at character without consuming"""
        idx = self.pos + offset
        if idx < len(self.code):
            return self.code[idx]
        return None
    
    def advance(self):
        """Move to next character"""
        if self.pos < len(self.code):
            char = self.code[self.pos]
            self.pos += 1
            if char == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            return char
        return None
    
    def skip_whitespace_inline(self):
        """Skip spaces and tabs on current line (NOT newlines)"""
        while self.peek() in (' ', '\t'):
            self.advance()
    
    def skip_comment(self):
        """Skip # comments"""
        if self.peek() == '#':
            while self.peek() and self.peek() != '\n':
                self.advance()
    
    def handle_indentation(self):
        """Handle line start indentation - emit INDENT/DEDENT tokens"""
        indent_level = 0
        while self.peek() == ' ':
            indent_level += 1
            self.advance()
        
        # Skip empty lines and comments
        if self.peek() == '\n' or self.peek() == '#':
            return
        
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            # Increased indentation
            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, None, self.line, self.col))
        elif indent_level < current_indent:
            # Decreased indentation
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, None, self.line, self.col))
            
            if self.indent_stack[-1] != indent_level:
                self.error(f"Indentation mismatch: expected {self.indent_stack[-1]}, got {indent_level}")
    
    def read_string(self):
        """Read string literal (supports ' and ")"""
        quote_char = self.advance()
        value = ""
        while True:
            char = self.peek()
            if char is None:
                self.error("Unterminated string")
            if char == quote_char:
                self.advance()
                break
            if char == '\\':
                self.advance()
                next_char = self.advance()
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                else:
                    value += next_char
            else:
                value += self.advance()
        return value
    
    def read_number(self):
        """Read number literal (int or float)"""
        value = ""
        while self.peek() and self.peek().isdigit():
            value += self.advance()
        if self.peek() == '.' and self.peek(1) and self.peek(1).isdigit():
            value += self.advance()
            while self.peek() and self.peek().isdigit():
                value += self.advance()
        return value
    
    def read_identifier(self):
        """Read identifier/keyword"""
        value = ""
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            value += self.advance()
        return value
    
    def tokenize(self):
        """Main tokenization loop"""
        while self.pos < len(self.code):
            # Handle indentation at line start
            if self.col == 1:
                self.handle_indentation()
            
            self.skip_whitespace_inline()
            
            if self.peek() is None:
                break
            
            # Comments
            if self.peek() == '#':
                self.skip_comment()
                if self.peek() == '\n':
                    self.advance()
                continue
            
            # Newline
            if self.peek() == '\n':
                self.advance()
                continue
            
            # Strings
            if self.peek() in ('"', "'"):
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, self.line, self.col))
                continue
            
            # Numbers
            if self.peek().isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, self.line, self.col))
                continue
            
            # Identifiers & Keywords
            if self.peek().isalpha() or self.peek() == '_':
                value = self.read_identifier()
                if value in self.KEYWORDS:
                    token_type = getattr(TokenType, value.upper())
                    self.tokens.append(Token(token_type, value, self.line, self.col))
                else:
                    self.tokens.append(Token(TokenType.IDENT, value, self.line, self.col))
                continue
            
            # Multi-character operators (check longer ones first!)
            two_char = self.peek() + (self.peek(1) or '')
            if two_char in self.OPERATORS:
                self.advance()
                self.advance()
                self.tokens.append(Token(self.OPERATORS[two_char], two_char, self.line, self.col))
                continue
            
            # Single-character operators
            one_char = self.peek()
            if one_char in self.OPERATORS:
                self.advance()
                self.tokens.append(Token(self.OPERATORS[one_char], one_char, self.line, self.col))
                continue
            
            self.error(f"Unknown character: {one_char}")
        
        # Emit remaining DEDENTs at end of file
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, None, self.line, self.col))
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return self.tokens