import sys
sys.path.insert(0, 'src')

from lexer import NexvoidLexer

with open('examples/test_protocol.nex', 'r') as f:
    code = f.read()

lexer = NexvoidLexer(code)
tokens = lexer.tokenize()

for i, t in enumerate(tokens):
    print(f'{i}: {t.type} {repr(t.value)} L{t.line}:C{t.col}')