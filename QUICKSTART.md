# Quick Start Guide

Get the CAD-P bot up and running in minutes.

## Prerequisites

- Python 3.8 or higher
- Git
- (Optional) Docker

## Installation

### Option 1: Local Installation (Recommended for Development)

```bash
# 1. Clone the repository
git clone <repository-url>
cd cad-p

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# Note: GDAL installation
# On Ubuntu/Debian:
sudo apt-get install gdal-bin libgdal-dev
pip install GDAL==$(gdal-config --version)

# On macOS:
brew install gdal
pip install GDAL==$(gdal-config --version)

# 4. Configure environment
cp .env.example .env
# Edit .env and add your bot token:
# BOT_TOKEN=your_token_from_botfather

# 5. Run the bot
python -m cad_p
```

### Option 2: Using Make

```bash
# Install dependencies
make install

# Configure .env
cp .env.example .env
# Edit .env and add your bot token

# Run the bot
make run
```

### Option 3: Using Docker (Easiest)

```bash
# 1. Clone and configure
git clone <repository-url>
cd cad-p
cp .env.example .env
# Edit .env and add your bot token

# 2. Build and run
docker-compose up -d

# 3. View logs
docker-compose logs -f
```

Or with Make:
```bash
make docker-compose
make docker-compose-logs
```

## Getting a Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Copy the token provided
5. Add it to `.env` file:
   ```
   BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

## Verify Installation

```bash
# Run verification script
python verify_scaffold.py

# Expected output:
# ============================================================
# CAD-P Project Scaffold Verification
# ============================================================
# ...
# Results: 30/30 checks passed
# ✓ All checks passed! Project scaffold is correctly set up.
```

## Running the Bot

### Start the Bot

```bash
# Using Python module
python -m cad_p

# Using Make
make run

# Using Docker Compose
docker-compose up

# Legacy method (backward compatible)
python bot_main.py
```

### Expected Output

When the bot starts successfully, you should see:

```
2024-01-01 12:00:00 - cad_p.bot - INFO - Starting CAD-P bot...
2024-01-01 12:00:00 - cad_p.bot - INFO - Ensuring required directories exist...
2024-01-01 12:00:00 - cad_p.bot - INFO - Initializing services...
2024-01-01 12:00:00 - cad_p.bot - INFO - Creating Telegram application...
2024-01-01 12:00:00 - cad_p.bot - INFO - Adding conversation handlers...
============================================================
CAD-P Bot Configuration:
  Log Level: INFO
  Debug Mode: False
  Development Mode: False
  Max File Size: 50 MB
  Max Points: 1,000,000
  Temp Directory: /path/to/project/temp/uploads
  Output Directory: /path/to/project/output
Feature Flags:
  Densification: True
  TIN: True
  Code Catalog: True
  File Validation: True
  Auto Encoding Detection: True
============================================================
2024-01-01 12:00:00 - cad_p.bot - INFO - Starting bot polling...
2024-01-01 12:00:00 - cad_p.bot - INFO - Bot is ready to receive messages!
```

## Testing the Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start` command
4. Follow the interactive prompts

## Development

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
# or
make install-dev
```

### Run Tests

```bash
pytest
# or
make test

# With coverage
make test-cov
```

### Code Quality

```bash
# Format code
make format

# Check formatting
make format-check

# Run linters
make lint
```

## Troubleshooting

### Bot Token Error

**Error**: `BOT_TOKEN not set`

**Solution**: Make sure `.env` file exists and contains your bot token:
```bash
cp .env.example .env
# Edit .env and add: BOT_TOKEN=your_actual_token
```

### GDAL Import Error

**Error**: `ModuleNotFoundError: No module named 'osgeo'`

**Solution**: Install system GDAL first:
```bash
# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev
pip install GDAL==$(gdal-config --version)

# macOS
brew install gdal
pip install GDAL==$(gdal-config --version)
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'cad_p'`

**Solution**: Make sure you're running from the project root:
```bash
cd /path/to/project
python -m cad_p
```

### Permission Errors

**Error**: Cannot write to logs/temp/output directories

**Solution**: The bot will try to create these automatically. If it fails:
```bash
mkdir -p logs temp output data
chmod 755 logs temp output data
```

## Next Steps

- Read [BOT_WORKFLOW.md](./BOT_WORKFLOW.md) to understand how the bot works
- Check [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
- See [INSTALLATION.md](./INSTALLATION.md) for detailed installation instructions
- Browse [docs/](./docs/) for user guides and API documentation

## Common Commands Reference

```bash
# Installation
pip install -r requirements.txt     # Install dependencies
make install                         # Install using Make
make install-dev                     # Install with dev dependencies

# Running
python -m cad_p                      # Run bot
make run                             # Run bot using Make
docker-compose up                    # Run bot in Docker

# Development
make test                            # Run tests
make lint                            # Check code quality
make format                          # Format code
make clean                           # Clean build artifacts

# Docker
make docker-build                    # Build Docker image
make docker-compose                  # Start with docker-compose
make docker-compose-logs             # View logs
make docker-compose-down             # Stop containers
```

## Support

- 📧 Email: support@example.com
- 💬 Telegram: @support_bot
- 🐛 Issues: GitHub Issues
- 📖 Documentation: [docs/](./docs/)
