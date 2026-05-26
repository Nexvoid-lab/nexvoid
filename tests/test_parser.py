# tests/test_parser.py
"""Test lexer + parser together"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from lexer import NexvoidLexer
from parser import NexvoidParser


def print_ast(node, indent=0):
    """Pretty print AST"""
    prefix = " " * indent
    print(f"{prefix}{node.__repr__()}")
    
    # Recursively print children
    if hasattr(node, 'statements'):
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    if hasattr(node, 'body') and node.body:
        if hasattr(node.body, 'statements'):
            for stmt in node.body.statements:
                print_ast(stmt, indent + 1)
    
    if hasattr(node, 'then_body') and node.then_body:
        print(f"{prefix} [THEN]")
        for stmt in node.then_body.statements:
            print_ast(stmt, indent + 2)
    
    if hasattr(node, 'else_body') and node.else_body:
        print(f"{prefix} [ELSE]")
        for stmt in node.else_body.statements:
            print_ast(stmt, indent + 2)
    
    if hasattr(node, 'expr'):
        print_ast(node.expr, indent + 1)
    
    if hasattr(node, 'left') and hasattr(node, 'right'):
        print(f"{prefix} LEFT:")
        print_ast(node.left, indent + 2)
        print(f"{prefix} RIGHT:")
        print_ast(node.right, indent + 2)


# Test 1: Basic variables and output
test1 = '''
name = "Nexvoid"
x = 5
cout(name)
cout(x)
'''

# Test 2: Function definition
test2 = '''
fun add(a, b)
    return a + b

result = add(5, 3)
cout(result)
'''

# Test 3: If statement
test3 = '''
x = 10
if x > 5
    cout("x is greater than 5")
else
    cout("x is less than or equal to 5")
'''

# Test 4: While loop
test4 = '''
x = 0
while x < 5
    cout(x)
    x = x + 1
'''

# Test 5: Repeat loop
test5 = '''
repeat 3 as i
    cout(i)
'''

# Test 6: Task and wait (async)
test6 = '''
task fetch_data()
    return "data"

result = wait fetch_data()
cout(result)
'''

# Test 7: Complex expression
test7 = '''
x = 5 + 3 * 2
y = (10 - 2) / 2
z = x > y and y < 10
cout(z)
'''

# Test 8: Pass statement
test8 = '''
if true
    pass
'''

# Test 9: Member access (module calls)
test9 = '''
model = ai.tensor.load("resnet50")
result = model.predict(x)
cout(result)
'''

# Test 10: Nested functions
test10 = '''
fun outer(x)
    fun inner(y)
        return x + y
    
    return inner(5)

cout(outer(10))
'''

tests = [
    ("Variables and Output", test1),
    ("Function Definition", test2),
    ("If Statement", test3),
    ("While Loop", test4),
    ("Repeat Loop", test5),
    ("Task and Wait", test6),
    ("Complex Expression", test7),
    ("Pass Statement", test8),
    ("Module Access", test9),
    ("Nested Functions", test10),
]

if __name__ == '__main__':
    for test_name, code in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        print("CODE:")
        print(code)
        print("\nAST:")
        
        try:
            # Lexer
            lexer = NexvoidLexer(code)
            tokens = lexer.tokenize()
            print(f"Tokens: {len(tokens)} tokens generated")
            
            # Parser
            parser = NexvoidParser(tokens)
            ast = parser.parse()
            
            # Print AST
            print_ast(ast)
            
            print("\n✓ PASSED")
        
        except Exception as e:
            print(f"\n✗ FAILED: {e}")
    
    print(f"\n{'='*60}")
    print("ALL TESTS COMPLETED")
    print(f"{'='*60}")
