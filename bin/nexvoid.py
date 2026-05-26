#!/usr/bin/env python3
# bin/nexvoid.py
"""Nexvoid interpreter - main CLI entry point with enhanced error handling"""

import sys
import os


# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import NexvoidLexer
from parser import NexvoidParser
from interpreter.core import NexvoidInterpreter
from module_loader import ModuleLoader


def print_error_context(error_msg, line=None, col=None, source_lines=None):
    """Print error with source context"""
    print(f"❌ Error: {error_msg}")
    
    if line is not None and col is not None:
        print(f" at line {line}, column {col}")
    
    if source_lines and line is not None:
        if 0 < line <= len(source_lines):
            source_line = source_lines[line - 1]
            print(f" {line} | {source_line}")
            if col is not None:
                print(f" | {' ' * (col - 1)}^")


def main():
    # Parse command line arguments
    force = '--force' in sys.argv
    if force:
        sys.argv.remove('--force')
    
    debug_mode = '--debug' in sys.argv
    if debug_mode:
        sys.argv.remove('--debug')

    if len(sys.argv) < 2:
        print("Usage: nexvoid [--force] <file.nex>")
        print("Example: nexvoid hello.nex")
        print(" nexvoid --force script.nex")
        print("\n--force: Skip file extension confirmation")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Validate file extension (.nex)
    if not filename.endswith('.nex'):
        if not force:
            print(f"⚠️ Warning: Expected .nex file, got '{filename}'")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
        else:
            print(f"⚠️ Warning: Expected .nex file, got '{filename}' (--force, continuing...)")
    
    try:
        # Read file
        try:
            with open(filename, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"❌ Error: File '{filename}' not found")
            sys.exit(1)
        
        source_lines = code.split('\n')
        
        print(f"[Nexvoid] Executing {filename}")
        print("-" * 60)
        
        # Lexer
        try:
            lexer = NexvoidLexer(code)
            tokens = lexer.tokenize()
        except SyntaxError as e:
            error_str = str(e)
            # Try to extract line/col from error message
            print_error_context(error_str, source_lines=source_lines)
            sys.exit(1)
        
        # Parser
        try:
            parser = NexvoidParser(tokens)
            ast = parser.parse()
        except SyntaxError as e:
            error_str = str(e)
            print_error_context(error_str, source_lines=source_lines)
            sys.exit(1)
        
        # Interpreter
        try:
            module_loader = ModuleLoader(stdlib_paths=["./stdlib"])
            interpreter = NexvoidInterpreter(module_loader=module_loader, debug=debug_mode)
            if debug_mode:
                print("[DEBUG] Starting interpretation with debug mode ON")
                print("=" * 60)
            interpreter.interpret(ast)
        except Exception as e:
            error_str = str(e)
            
            # Try to extract line/col from error if available
            if hasattr(e, 'line') and hasattr(e, 'col'):
                print_error_context(
                    e.msg if hasattr(e, 'msg') else error_str,
                    line=e.line,
                    col=e.col,
                    source_lines=source_lines
                )
            else:
                print_error_context(error_str, source_lines=source_lines)
            sys.exit(1)
        
        print("-" * 60)
        print("[Nexvoid] Execution complete sir! 🎉")
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n[Nexvoid] ⏸ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
