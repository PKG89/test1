# Architecture Overview

This document describes the architecture and structure of the CAD-P bot project.

## Project Structure

```
cad-p/
├── src/cad_p/              # Main application package
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Entry point for `python -m cad_p`
│   ├── bot.py              # Bot startup and initialization
│   ├── config.py           # Configuration management
│   ├── logging_config.py   # Logging setup
│   ├── dependencies.py     # Dependency injection container
│   │
│   ├── bot/                # Telegram bot handlers
│   │   ├── handlers.py     # Message and callback handlers
│   │   ├── conversation.py # Conversation flow
│   │   ├── file_parser.py  # File parsing utilities
│   │   └── states.py       # Conversation states
│   │
│   ├── services/           # Business logic services
│   │   ├── processing_service.py    # Main processing orchestrator
│   │   ├── tin_service.py           # TIN generation
│   │   ├── densification_service.py # Point densification
│   │   ├── rule_engine.py           # Code catalog rules
│   │   └── catalog_workflow.py      # Code catalog workflow
│   │
│   ├── models/             # Domain models and data structures
│   │   ├── settings.py     # Project settings
│   │   ├── point_data.py   # Point data models
│   │   ├── bot_data.py     # Bot state data
│   │   └── rule_data.py    # Rule engine data
│   │
│   ├── dxf/                # DXF file handling
│   │   └── ...
│   │
│   ├── processors/         # Data processors
│   │   └── ...
│   │
│   ├── catalog/            # Code catalog
│   │   └── ...
│   │
│   └── utils/              # Utility functions
│       └── ...
│
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test fixtures
│
├── docs/                   # Documentation
├── templates/              # DXF templates
├── examples/               # Example files
├── logs/                   # Log files (gitignored)
├── temp/                   # Temporary uploads (gitignored)
├── output/                 # Generated files (gitignored)
├── data/                   # Persistent data (gitignored)
│
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml         # Modern Python project config
├── setup.py               # Legacy setup file
├── .env.example           # Environment variables template
├── Makefile               # Development tasks
├── Dockerfile             # Container image
├── docker-compose.yaml    # Container orchestration
└── README.md              # Project overview

```

## Core Components

### 1. Configuration (`config.py`)

Centralized configuration management using environment variables:
- Bot tokens and credentials
- File paths and directories
- Feature toggles
- Performance settings
- Development/debug flags

All configuration is loaded from `.env` file using python-dotenv.

### 2. Logging (`logging_config.py`)

Configurable logging system:
- Console and file output
- Configurable log levels
- Structured log format
- Library-specific log filtering

### 3. Dependency Injection (`dependencies.py`)

Simple service container pattern:
- Centralized service instantiation
- Lazy initialization
- Easy testing and mocking
- Clean separation of concerns

### 4. Bot Module (`bot.py`)

Main entry point that:
- Initializes logging
- Validates configuration
- Creates required directories
- Registers services
- Sets up Telegram handlers
- Starts polling loop

## Service Architecture

### Processing Pipeline

```
User → Telegram Bot → Handlers → Services → Processors → DXF Output
                                    ↓
                              Domain Models
```

### Service Layer

**ProcessingService**: Orchestrates the entire processing pipeline
- Coordinates between different services
- Handles error recovery
- Manages temporary files

**TINService**: Triangulation and terrain modeling
- Delaunay triangulation
- Breakline handling
- Triangle filtering

**DensificationService**: Point cloud densification
- Grid-based interpolation
- Multiple interpolation methods
- Quality control

**RuleEngine**: Code catalog and rule processing
- Code pattern matching
- Label generation
- Special behavior handling

**CatalogWorkflow**: High-level code catalog operations
- Code classification
- Block generation
- Layer assignment

## Data Flow

### 1. File Upload
```
User uploads file → Bot receives → Save to temp → Parse file
```

### 2. Validation
```
Parse file → Detect encoding → Validate format → Check data quality
```

### 3. Processing
```
Load points → Apply filters → Build TIN → Densify → Apply catalog rules
```

### 4. Output Generation
```
Process results → Generate DXF → Add blocks/labels → Return to user
```

## Configuration Management

### Environment Variables

All configuration is managed through environment variables (`.env` file):

```env
# Required
BOT_TOKEN=xxx

# Optional with defaults
LOG_LEVEL=INFO
TEMP_DIR=temp/uploads
MAX_FILE_SIZE_MB=50
ENABLE_DENSIFICATION=true
```

### Feature Toggles

Feature toggles allow enabling/disabling functionality:
- `ENABLE_DENSIFICATION`: Point densification
- `ENABLE_TIN`: TIN generation
- `ENABLE_CODE_CATALOG`: Code catalog processing
- `ENABLE_FILE_VALIDATION`: Input validation
- `ENABLE_AUTO_ENCODING_DETECTION`: Encoding detection

## Testing Strategy

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Fast execution

### Integration Tests
- Test service interactions
- Use test fixtures
- Validate end-to-end workflows

### Test Structure
```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_services.py
│   └── test_processors.py
├── integration/
│   ├── test_processing_pipeline.py
│   └── test_bot_workflow.py
└── fixtures/
    ├── sample_data.txt
    └── template.dxf
```

## Deployment

### Docker

Multi-stage build:
1. **Builder stage**: Install build dependencies, compile packages
2. **Runtime stage**: Copy artifacts, install runtime deps only

Benefits:
- Smaller image size
- Faster deployment
- Reproducible builds
- Includes GDAL support

### Docker Compose

Local development setup:
- Automatic restarts
- Volume mounts for development
- Log management
- Easy configuration

## Extension Points

### Adding a New Service

1. Create service in `src/cad_p/services/`
2. Register in `dependencies.py`
3. Add configuration to `config.py`
4. Write tests

### Adding a New Handler

1. Create handler in `src/cad_p/bot/`
2. Register in `handlers.py`
3. Add state if needed in `states.py`
4. Update conversation flow

### Adding a New Processor

1. Create processor in `src/cad_p/processors/`
2. Integrate with processing service
3. Add domain models if needed
4. Write tests

## Best Practices

1. **Configuration**: Use environment variables for all config
2. **Logging**: Use structured logging with appropriate levels
3. **Error Handling**: Catch and log errors, provide user feedback
4. **Testing**: Write tests for new functionality
5. **Documentation**: Update docs when adding features
6. **Code Style**: Follow PEP 8, use type hints
7. **Dependencies**: Pin versions, document system deps

## Development Workflow

```bash
# Setup
make install-dev

# Code
# ... make changes ...

# Test
make test

# Format
make format

# Lint
make lint

# Run
make run
```

## Performance Considerations

1. **File Processing**: Stream large files, don't load entirely into memory
2. **TIN Generation**: Use efficient algorithms (scipy.spatial.Delaunay)
3. **Caching**: Cache expensive computations when appropriate
4. **Async**: Use async/await for I/O operations
5. **Threading**: Use worker threads for CPU-bound tasks

## Security

1. **Environment Variables**: Never commit `.env` file
2. **Bot Token**: Keep token secret, rotate if compromised
3. **File Uploads**: Validate and sanitize all uploads
4. **User Input**: Sanitize user input before processing
5. **Docker**: Run as non-root user, minimal image
