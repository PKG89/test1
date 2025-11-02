# Development Guide

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run CLI
python cli.py examples/sample_coordinates.txt output/test.dxf --densify
```

## Architecture

- **src/bot/** - Telegram bot handlers
- **src/processors/** - Data processing (points, TIN, densification)
- **src/dxf/** - DXF export and layer management
- **src/services/** - Business logic
- **src/models/** - Data models
- **tests/** - Unit and integration tests

## Key Patterns

### ezdxf API Usage

```python
# Text positioning - CORRECT
text = msp.add_text(
    "text",
    dxfattribs={
        'insert': (x, y),
        'halign': 1  # centered
    }
)

# Polylines - CORRECT
msp.add_lwpolyline(points, close=True, dxfattribs={'layer': 'name'})
```

### Layer Names (Russian)

- "1 исходная поверхность" - Original surface (color 7)
- "1 пикеты исходные" - Original points (color 7)
- "2 отредактированная поверхность" - Densified surface (color 1/red)
- "2 пикеты добавленные" - Generated points (color 1/red)

## Testing

```bash
# All tests
pytest tests/ -v

# Specific suite
pytest tests/test_densification.py -v
pytest tests/test_layer_assignment.py -v
pytest tests/test_integration.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Code Style

- Docstrings for all public functions
- Type hints throughout
- snake_case for functions/variables
- PascalCase for classes
- Russian for user messages, English for code
