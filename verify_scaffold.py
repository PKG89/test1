#!/usr/bin/env python3
"""Verify that the project scaffold is correctly set up."""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Check if a file exists."""
    if Path(path).exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} - NOT FOUND")
        return False

def check_directory(path, description):
    """Check if a directory exists."""
    if Path(path).is_dir():
        print(f"✓ {description}: {path}/")
        return True
    else:
        print(f"✗ {description}: {path}/ - NOT FOUND")
        return False

def main():
    """Run scaffold verification checks."""
    print("=" * 60)
    print("CAD-P Project Scaffold Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    # Check configuration files
    print("Configuration Files:")
    checks.append(check_file("requirements.txt", "Requirements file"))
    checks.append(check_file("requirements-dev.txt", "Dev requirements file"))
    checks.append(check_file("pyproject.toml", "PyProject TOML"))
    checks.append(check_file("setup.py", "Setup.py"))
    checks.append(check_file(".env.example", "Environment example"))
    checks.append(check_file(".gitignore", "Gitignore"))
    checks.append(check_file("Makefile", "Makefile"))
    checks.append(check_file("Dockerfile", "Dockerfile"))
    checks.append(check_file("docker-compose.yaml", "Docker Compose"))
    checks.append(check_file(".dockerignore", "Docker ignore"))
    checks.append(check_file("INSTALLATION.md", "Installation guide"))
    print()
    
    # Check directory structure
    print("Directory Structure:")
    checks.append(check_directory("src/cad_p", "Main package directory"))
    checks.append(check_directory("src/cad_p/bot", "Bot handlers"))
    checks.append(check_directory("src/cad_p/services", "Services"))
    checks.append(check_directory("src/cad_p/models", "Domain models"))
    checks.append(check_directory("src/cad_p/utils", "Utilities"))
    checks.append(check_directory("tests", "Tests"))
    checks.append(check_directory("docs", "Documentation"))
    checks.append(check_directory("templates", "Templates"))
    checks.append(check_directory("logs", "Logs directory"))
    checks.append(check_directory("temp", "Temp directory"))
    checks.append(check_directory("output", "Output directory"))
    checks.append(check_directory("data", "Data directory"))
    print()
    
    # Check core module files
    print("Core Module Files:")
    checks.append(check_file("src/cad_p/__init__.py", "Package init"))
    checks.append(check_file("src/cad_p/__main__.py", "Main entry point"))
    checks.append(check_file("src/cad_p/bot.py", "Bot module"))
    checks.append(check_file("src/cad_p/config.py", "Configuration module"))
    checks.append(check_file("src/cad_p/logging_config.py", "Logging configuration"))
    checks.append(check_file("src/cad_p/dependencies.py", "Dependency injection"))
    print()
    
    # Check if main module can be imported (without dependencies)
    print("Import Checks:")
    try:
        sys.path.insert(0, 'src')
        import cad_p
        print("✓ Package can be imported")
        checks.append(True)
    except ImportError as e:
        print(f"✗ Package import failed: {e}")
        checks.append(False)
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ All checks passed! Project scaffold is correctly set up.")
        print()
        print("Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure .env: cp .env.example .env")
        print("  3. Run the bot: python -m cad_p")
        return 0
    else:
        print("✗ Some checks failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
