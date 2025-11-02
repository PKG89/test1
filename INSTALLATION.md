# Installation Guide

This guide provides detailed instructions for installing and setting up the CAD-P bot.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Docker (optional, for containerized deployment)

## System Dependencies

### GDAL Installation

GDAL is required for geospatial operations. Install it before installing Python packages.

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev python3-dev
```

#### macOS (using Homebrew)

```bash
brew install gdal
```

#### Windows

Download and install from: https://www.gisinternals.com/release.php

Or use conda:
```bash
conda install -c conda-forge gdal
```

## Installation Methods

### Method 1: Using pip and requirements.txt

1. Clone the repository:
```bash
git clone <repository-url>
cd cad-p
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install GDAL Python bindings (after system GDAL is installed):
```bash
pip install GDAL==$(gdal-config --version)
```

### Method 2: Using pip and pyproject.toml

1. Clone the repository:
```bash
git clone <repository-url>
cd cad-p
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in editable mode:
```bash
pip install -e .
```

### Method 3: Using Make

```bash
make install
```

For development installation:
```bash
make install-dev
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and set your Telegram bot token:
```env
BOT_TOKEN=your_token_from_botfather
```

To get a bot token:
- Open Telegram and search for @BotFather
- Send `/newbot` command and follow instructions
- Copy the token provided

3. Customize other settings in `.env` as needed (see `.env.example` for all options)

## Running the Bot

### Method 1: Using Python module

```bash
python -m cad_p
```

### Method 2: Using Make

```bash
make run
```

### Method 3: Using the installed script

```bash
cad-p
```

## Docker Installation

### Building the Docker Image

```bash
docker build -t cad-p-bot:latest .
```

Or using Make:
```bash
make docker-build
```

### Running with Docker

```bash
docker run --rm --env-file .env cad-p-bot:latest
```

Or using Make:
```bash
make docker-run
```

### Using Docker Compose

1. Ensure `.env` file is configured

2. Start the bot:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f
```

4. Stop the bot:
```bash
docker-compose down
```

Or using Make:
```bash
make docker-compose        # Start
make docker-compose-logs   # View logs
make docker-compose-down   # Stop
```

## Development Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

Or:
```bash
make install-dev
```

2. Run tests:
```bash
pytest
```

Or:
```bash
make test
```

3. Run linting:
```bash
make lint
```

4. Format code:
```bash
make format
```

## Troubleshooting

### GDAL Installation Issues

If you encounter GDAL-related errors:

1. Ensure system GDAL is installed:
```bash
gdal-config --version
```

2. Install Python GDAL bindings matching your system version:
```bash
pip install GDAL==$(gdal-config --version)
```

### Import Errors

If you get import errors, ensure you're running from the project root and the virtual environment is activated:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Bot Token Issues

Ensure your `.env` file contains a valid bot token:
- The token should look like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- Check that the `.env` file is in the project root
- Verify no extra spaces or quotes around the token

## Verification

To verify the installation:

1. Check that all dependencies are installed:
```bash
pip list
```

2. Run a quick test:
```bash
python -c "import cad_p; print('Installation successful!')"
```

3. Start the bot (it will log configuration and startup messages):
```bash
python -m cad_p
```

You should see output like:
```
2024-01-01 12:00:00 - cad_p.bot - INFO - Starting CAD-P bot...
2024-01-01 12:00:00 - cad_p.bot - INFO - Ensuring required directories exist...
2024-01-01 12:00:00 - cad_p.bot - INFO - Initializing services...
...
2024-01-01 12:00:00 - cad_p.bot - INFO - Bot is ready to receive messages!
```

## Next Steps

- Read the [User Guide](./docs/user-guide.md) to learn how to use the bot
- Check [BOT_WORKFLOW.md](./BOT_WORKFLOW.md) for workflow details
- See [DEVELOPMENT.md](./DEVELOPMENT.md) for development guidelines
