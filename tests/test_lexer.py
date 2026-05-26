# tests/test_lexer.py
"""Unit tests for Nexvoid lexer"""

import sys
import os

# Add src to path so we can import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from lexer import NexvoidLexer
from tokens import TokenType


def test_basic_function():
    """Test: fun greet(name)"""
    code = "fun greet(name)"
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.FUN
    assert tokens[1].type == TokenType.IDENT
    assert tokens[1].value == "greet"
    assert tokens[2].type == TokenType.LPAREN
    assert tokens[3].type == TokenType.IDENT
    assert tokens[3].value == "name"
    assert tokens[4].type == TokenType.RPAREN
    print("✓ test_basic_function passed")


def test_string_literal():
    """Test: "Hello Nexvoid" """
    code = '"Hello Nexvoid"'
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "Hello Nexvoid"
    print("✓ test_string_literal passed")


def test_numbers():
    """Test: 42 and 3.14"""
    code = "42 3.14"
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == "42"
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].value == "3.14"
    print("✓ test_numbers passed")


def test_operators():
    """Test: + - * / == != < > <= >="""
    code = "+ - * / == != < > <= >="
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.PLUS
    assert tokens[1].type == TokenType.MINUS
    assert tokens[2].type == TokenType.MULT
    assert tokens[3].type == TokenType.DIV
    assert tokens[4].type == TokenType.EQ
    assert tokens[5].type == TokenType.NE
    assert tokens[6].type == TokenType.LT
    assert tokens[7].type == TokenType.GT
    assert tokens[8].type == TokenType.LE
    assert tokens[9].type == TokenType.GE
    print("✓ test_operators passed")


def test_keywords():
    """Test: fun task wait return if else"""
    code = "fun task wait return if else"
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.FUN
    assert tokens[1].type == TokenType.TASK
    assert tokens[2].type == TokenType.WAIT
    assert tokens[3].type == TokenType.RETURN
    assert tokens[4].type == TokenType.IF
    assert tokens[5].type == TokenType.ELSE
    print("✓ test_keywords passed")


def test_module_access():
    """Test: ai.tensor.load"""
    code = "ai.tensor.load"
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.IDENT
    assert tokens[0].value == "ai"
    assert tokens[1].type == TokenType.DOT
    assert tokens[2].type == TokenType.IDENT
    assert tokens[2].value == "tensor"
    assert tokens[3].type == TokenType.DOT
    assert tokens[4].type == TokenType.IDENT
    assert tokens[4].value == "load"
    print("✓ test_module_access passed")


def test_cout_string_concat():
    """Test: cout("Hello " + name)"""
    code = 'cout("Hello " + name)'
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.COUT
    assert tokens[1].type == TokenType.LPAREN
    assert tokens[2].type == TokenType.STRING
    assert tokens[3].type == TokenType.PLUS
    assert tokens[4].type == TokenType.IDENT
    assert tokens[5].type == TokenType.RPAREN
    print("✓ test_cout_string_concat passed")


def test_indentation_simple():
    """Test: simple function with indentation"""
    code = """fun greet(name)
    cout("Hello")"""
    
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    # Should have: FUN, IDENT, LPAREN, IDENT, RPAREN, IDENT, COUT, ...
    assert tokens[0].type == TokenType.FUN
    assert tokens[5].type == TokenType.IDENT
    assert tokens[6].type == TokenType.COUT
    print("✓ test_indentation_simple passed")


def test_indentation_dedent():
    """Test: indentation and dedentation"""
    code = """fun greet(name)
    cout("Hello")

x = 5"""
    
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    # Find DEDENT token
    dedent_found = False
    for token in tokens:
        if token.type == TokenType.DEDENT:
            dedent_found = True
            break
    
    assert dedent_found, "DEDENT token not found"
    print("✓ test_indentation_dedent passed")


def test_nested_indentation():
    """Test: nested if inside function"""
    code = """fun test()
    if true
        cout("nested")"""
    
    lexer = NexvoidLexer(code)
    tokens = lexer.tokenize()
    
    indent_count = sum(1 for t in tokens if t.type == TokenType.IDENT)
    assert indent_count == 2, f"Expected 2 IDENTs, got {indent_count}"
    print("✓ test_nested_indentation passed")


if __name__ == '__main__':
    try:
        test_basic_function()
        test_string_literal()
        test_numbers()
        test_operators()
        test_keywords()
        test_module_access()
        test_cout_string_concat()
        test_indentation_simple()
        test_indentation_dedent()
        test_nested_indentation()
        print("\n" + "="*50)
        print("ALL TESTS PASSED! ✓")
        print("="*50)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)