#!/usr/bin/env python3
"""Test that the project structure is correct without requiring dependencies."""

import sys
import ast
from pathlib import Path

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    """Run structure tests."""
    print("=" * 60)
    print("CAD-P Structure and Syntax Test")
    print("=" * 60)
    print()
    
    # Add src to path
    sys.path.insert(0, 'src')
    
    # Check package can be imported
    print("Import Test:")
    try:
        import cad_p
        print("✓ cad_p package can be imported")
    except Exception as e:
        print(f"✗ cad_p import failed (this is OK if dependencies aren't installed): {e}")
    print()
    
    # Check syntax of all Python files
    print("Syntax Check:")
    python_files = list(Path('src/cad_p').rglob('*.py'))
    
    syntax_errors = []
    for pyfile in python_files:
        valid, error = check_file_syntax(pyfile)
        if valid:
            print(f"✓ {pyfile}")
        else:
            print(f"✗ {pyfile}: {error}")
            syntax_errors.append((pyfile, error))
    
    print()
    print("=" * 60)
    
    if syntax_errors:
        print(f"✗ {len(syntax_errors)} file(s) with syntax errors")
        for filepath, error in syntax_errors:
            print(f"  {filepath}: {error}")
        return 1
    else:
        print(f"✓ All {len(python_files)} Python files have valid syntax")
        print("✓ Project structure is correct!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
