.PHONY: help install install-dev test lint format clean run docker-build docker-run

help:
	@echo "CAD-P Bot - Available Commands"
	@echo "================================"
	@echo "install         - Install production dependencies"
	@echo "install-dev     - Install development dependencies"
	@echo "test            - Run tests with pytest"
	@echo "test-cov        - Run tests with coverage report"
	@echo "lint            - Run linting checks (flake8, mypy)"
	@echo "format          - Format code with black and isort"
	@echo "format-check    - Check code formatting without changes"
	@echo "clean           - Remove build artifacts and cache files"
	@echo "run             - Run the bot"
	@echo "docker-build    - Build Docker image"
	@echo "docker-run      - Run bot in Docker container"
	@echo "docker-compose  - Run bot with docker-compose"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src/cad_p --cov-report=html --cov-report=term

lint:
	@echo "Running flake8..."
	flake8 src/cad_p tests --max-line-length=100 --extend-ignore=E203,W503
	@echo "Running mypy..."
	mypy src/cad_p --ignore-missing-imports

format:
	@echo "Running black..."
	black src/cad_p tests
	@echo "Running isort..."
	isort src/cad_p tests

format-check:
	@echo "Checking black formatting..."
	black --check src/cad_p tests
	@echo "Checking isort..."
	isort --check-only src/cad_p tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist htmlcov .coverage

run:
	python -m cad_p

docker-build:
	docker build -t cad-p-bot:latest .

docker-run:
	docker run --rm --env-file .env cad-p-bot:latest

docker-compose:
	docker-compose up -d

docker-compose-logs:
	docker-compose logs -f

docker-compose-down:
	docker-compose down
