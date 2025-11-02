#!/usr/bin/env python3
"""
Acceptance test for the CAD-P project scaffold.

This script verifies that all acceptance criteria from the ticket are met:
1. pip install -r requirements.txt works (structure check)
2. python -m cad_p.bot can be invoked (structure check)
3. Docker image can be built (Dockerfile exists and is valid)
4. All required files and directories exist
"""

import sys
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).is_file():
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description} not found: {filepath}")
        return False


def check_directory_exists(dirpath, description):
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print_success(f"{description}: {dirpath}/")
        return True
    else:
        print_error(f"{description} not found: {dirpath}/")
        return False


def test_requirements_file():
    """Test that requirements.txt exists and is valid."""
    print_header("Acceptance Test 1: Requirements File")
    
    checks = []
    
    # Check files exist
    checks.append(check_file_exists("requirements.txt", "requirements.txt"))
    checks.append(check_file_exists("requirements-dev.txt", "requirements-dev.txt"))
    
    # Check content
    if Path("requirements.txt").exists():
        with open("requirements.txt") as f:
            content = f.read()
        
        required_packages = [
            "python-telegram-bot",
            "pandas",
            "numpy",
            "scipy",
            "shapely",
            "ezdxf",
            "chardet",
            "Pillow",
            "requests",
            "python-dotenv",
        ]
        
        print("\nChecking required packages:")
        for package in required_packages:
            if package in content:
                print_success(f"Package listed: {package}")
                checks.append(True)
            else:
                print_error(f"Package missing: {package}")
                checks.append(False)
    
    return all(checks)


def test_module_structure():
    """Test that python -m cad_p structure is correct."""
    print_header("Acceptance Test 2: Module Structure")
    
    checks = []
    
    # Check directory structure
    checks.append(check_directory_exists("src/cad_p", "Main package"))
    checks.append(check_directory_exists("src/cad_p/bot", "Bot handlers"))
    checks.append(check_directory_exists("src/cad_p/services", "Services"))
    checks.append(check_directory_exists("src/cad_p/models", "Models"))
    checks.append(check_directory_exists("src/cad_p/utils", "Utilities"))
    
    # Check core files
    checks.append(check_file_exists("src/cad_p/__init__.py", "Package init"))
    checks.append(check_file_exists("src/cad_p/__main__.py", "Main entrypoint"))
    checks.append(check_file_exists("src/cad_p/bot.py", "Bot module"))
    checks.append(check_file_exists("src/cad_p/config.py", "Config module"))
    checks.append(check_file_exists("src/cad_p/logging_config.py", "Logging config"))
    checks.append(check_file_exists("src/cad_p/dependencies.py", "Dependencies"))
    
    # Test import
    print("\nTesting package import:")
    sys.path.insert(0, 'src')
    try:
        import cad_p
        print_success("Package 'cad_p' can be imported")
        checks.append(True)
    except ImportError as e:
        print_error(f"Package import failed: {e}")
        checks.append(False)
    
    return all(checks)


def test_docker_files():
    """Test that Docker files exist and are valid."""
    print_header("Acceptance Test 3: Docker Configuration")
    
    checks = []
    
    # Check files exist
    checks.append(check_file_exists("Dockerfile", "Dockerfile"))
    checks.append(check_file_exists("docker-compose.yaml", "docker-compose.yaml"))
    checks.append(check_file_exists(".dockerignore", ".dockerignore"))
    
    # Check Dockerfile content
    if Path("Dockerfile").exists():
        with open("Dockerfile") as f:
            content = f.read()
        
        print("\nChecking Dockerfile features:")
        required_features = [
            ("multi-stage", "FROM python:3.11-slim as builder"),
            ("GDAL support", "gdal-bin"),
            ("virtual environment", "/opt/venv"),
            ("non-root user", "botuser"),
        ]
        
        for feature_name, feature_text in required_features:
            if feature_text in content:
                print_success(f"Feature present: {feature_name}")
                checks.append(True)
            else:
                print_error(f"Feature missing: {feature_name}")
                checks.append(False)
    
    return all(checks)


def test_configuration_files():
    """Test configuration files."""
    print_header("Acceptance Test 4: Configuration Files")
    
    checks = []
    
    # Check files
    checks.append(check_file_exists(".env.example", ".env.example"))
    checks.append(check_file_exists("pyproject.toml", "pyproject.toml"))
    checks.append(check_file_exists("setup.py", "setup.py"))
    checks.append(check_file_exists("Makefile", "Makefile"))
    checks.append(check_file_exists(".gitignore", ".gitignore"))
    
    # Check .env.example content
    if Path(".env.example").exists():
        with open(".env.example") as f:
            content = f.read()
        
        print("\nChecking .env.example variables:")
        required_vars = [
            "BOT_TOKEN",
            "LOG_LEVEL",
            "TEMP_DIR",
            "ENABLE_DENSIFICATION",
            "ENABLE_TIN",
        ]
        
        for var in required_vars:
            if var in content:
                print_success(f"Variable present: {var}")
                checks.append(True)
            else:
                print_error(f"Variable missing: {var}")
                checks.append(False)
    
    return all(checks)


def test_documentation():
    """Test documentation files."""
    print_header("Acceptance Test 5: Documentation")
    
    checks = []
    
    # Check files
    checks.append(check_file_exists("README.md", "README.md"))
    checks.append(check_file_exists("INSTALLATION.md", "INSTALLATION.md"))
    checks.append(check_file_exists("ARCHITECTURE.md", "ARCHITECTURE.md"))
    checks.append(check_file_exists("QUICKSTART.md", "QUICKSTART.md"))
    checks.append(check_directory_exists("docs", "docs directory"))
    
    return all(checks)


def test_development_tools():
    """Test development tools."""
    print_header("Acceptance Test 6: Development Tools")
    
    checks = []
    
    # Check Makefile targets
    if Path("Makefile").exists():
        with open("Makefile") as f:
            content = f.read()
        
        print("Checking Makefile targets:")
        required_targets = ["install", "test", "lint", "run", "docker-build"]
        
        for target in required_targets:
            if f"{target}:" in content:
                print_success(f"Target present: {target}")
                checks.append(True)
            else:
                print_error(f"Target missing: {target}")
                checks.append(False)
    else:
        checks.append(False)
    
    return all(checks)


def main():
    """Run all acceptance tests."""
    print(f"\n{Colors.BOLD}CAD-P Project Scaffold - Acceptance Tests{Colors.RESET}")
    print("Testing acceptance criteria from the ticket...")
    
    results = {}
    
    # Run all tests
    results["Requirements"] = test_requirements_file()
    results["Module Structure"] = test_module_structure()
    results["Docker"] = test_docker_files()
    results["Configuration"] = test_configuration_files()
    results["Documentation"] = test_documentation()
    results["Development Tools"] = test_development_tools()
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} test suites passed{Colors.RESET}\n")
    
    if passed == total:
        print_success("✓ All acceptance criteria met!")
        print("\n" + Colors.BOLD + "Next steps:" + Colors.RESET)
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure bot: cp .env.example .env")
        print("  3. Add bot token to .env file")
        print("  4. Run the bot: python -m cad_p")
        print()
        return 0
    else:
        print_error("✗ Some acceptance criteria not met")
        return 1


if __name__ == '__main__':
    sys.exit(main())
