# CAD-P Documentation

Welcome to the CAD-P bot documentation. This directory contains comprehensive guides for users and developers.

## Quick Links

- [Quick Start Guide](../QUICKSTART.md) - Get up and running in minutes
- [Installation Guide](../INSTALLATION.md) - Detailed installation instructions
- [Architecture Overview](../ARCHITECTURE.md) - System design and components
- [Bot Workflow](../BOT_WORKFLOW.md) - How the Telegram bot works

## Documentation Structure

### User Documentation

- **[User Guide](./user-guide.md)** - Complete guide for bot users
  - How to use the bot
  - Preparing input files
  - Understanding output
  - Troubleshooting

- **[Bot Workflow](../BOT_WORKFLOW.md)** - Telegram bot interaction flow
  - Conversation states
  - Available commands
  - File upload process

- **[Code Catalog Guide](./code-catalog.md)** - Understanding code catalog
  - 60+ supported codes
  - Rule types and behaviors
  - Custom code configuration

### Developer Documentation

- **[Architecture Overview](../ARCHITECTURE.md)** - System architecture
  - Project structure
  - Component overview
  - Design patterns

- **[Developer Guide](./developer-guide.md)** - Development guidelines
  - Setting up development environment
  - Code organization
  - Adding new features
  - Testing strategy

- **[API Documentation](./api.md)** - Code reference
  - Service APIs
  - Model definitions
  - Utility functions

### Feature Documentation

- **[TIN Feature](../TIN_FEATURE_SUMMARY.md)** - Triangulation network
  - TIN generation
  - Breakline handling
  - Quality control

- **[Densification Feature](../DENSIFICATION_FEATURE.md)** - Point densification
  - Algorithm overview
  - Interpolation methods
  - Configuration options

- **[Code Catalog Feature](../CODE_CATALOG_FEATURE.md)** - Code processing
  - Code rules
  - Block generation
  - Layer management

- **[Geometry Engine](../GEOMETRY_ENGINE.md)** - Geometric operations
  - Spatial algorithms
  - Coordinate systems
  - Transformations

### Deployment Documentation

- **[Deployment Guide](./deployment.md)** - Production deployment
  - Docker deployment
  - Environment configuration
  - Monitoring and logging
  - Scaling considerations

- **[Docker Guide](../Dockerfile)** - Container setup
  - Multi-stage build
  - GDAL installation
  - Volume management

## Getting Started

### For Users

1. Read the [Quick Start Guide](../QUICKSTART.md)
2. Follow the [Installation Guide](../INSTALLATION.md)
3. Check the [Bot Workflow](../BOT_WORKFLOW.md)
4. Explore the [User Guide](./user-guide.md)

### For Developers

1. Set up your environment following [Installation Guide](../INSTALLATION.md)
2. Read the [Architecture Overview](../ARCHITECTURE.md)
3. Study the [Developer Guide](./developer-guide.md)
4. Review existing code and tests
5. Check [DEVELOPMENT.md](../DEVELOPMENT.md) for contribution guidelines

## Key Concepts

### Project Structure

```
cad-p/
├── src/cad_p/          # Main application code
│   ├── bot/            # Telegram bot handlers
│   ├── services/       # Business logic
│   ├── models/         # Data models
│   ├── processors/     # Data processors
│   ├── dxf/            # DXF generation
│   ├── catalog/        # Code catalog
│   └── utils/          # Utilities
├── tests/              # Test suite
├── docs/               # Documentation (you are here)
└── templates/          # DXF templates
```

### Core Components

1. **Bot Module** - Telegram bot interface
2. **Services** - Business logic and processing
3. **Models** - Data structures and domain objects
4. **Processors** - Data transformation and processing
5. **DXF Module** - CAD file generation

### Configuration

All configuration is managed through environment variables:
- `.env` file for local configuration
- Environment variables in production
- Feature toggles for functionality

See [.env.example](../.env.example) for all available options.

## Development Workflow

```bash
# Setup
make install-dev

# Development
# ... edit code ...

# Test
make test

# Format
make format

# Lint
make lint

# Run
make run
```

## Testing

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **Syntax Tests**: Validate Python syntax
- **Structure Tests**: Verify project structure

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run structure verification
python verify_scaffold.py
```

## Common Tasks

### Adding a New Feature

1. Design the feature and update documentation
2. Create domain models in `models/`
3. Implement service logic in `services/`
4. Add bot handlers if needed in `bot/`
5. Write tests
6. Update configuration if needed
7. Document the feature

### Updating Dependencies

1. Update version in `requirements.txt` or `pyproject.toml`
2. Test compatibility
3. Update documentation if needed
4. Rebuild Docker image if using containers

### Debugging

- Check logs in `logs/bot.log`
- Set `LOG_LEVEL=DEBUG` in `.env`
- Use `DEVELOPMENT_MODE=true` for extra logging
- Review error messages in bot responses

## Resources

### External Documentation

- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/) - Bot framework
- [ezdxf](https://ezdxf.readthedocs.io/) - DXF library
- [NumPy](https://numpy.org/doc/) - Numerical computing
- [SciPy](https://scipy.org/doc/) - Scientific computing
- [Shapely](https://shapely.readthedocs.io/) - Geometric operations
- [GDAL](https://gdal.org/api/python.html) - Geospatial data

### Project Links

- Repository: [GitHub](https://github.com/yourusername/cad-p)
- Issues: [GitHub Issues](https://github.com/yourusername/cad-p/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/cad-p/discussions)

## Support

- 📧 Email: support@example.com
- 💬 Telegram: @support_bot
- 🐛 Issues: GitHub Issues
- 📖 Documentation: You are here!

## Contributing

We welcome contributions! Please:

1. Read [DEVELOPMENT.md](../DEVELOPMENT.md)
2. Check existing issues or create a new one
3. Fork the repository
4. Create a feature branch
5. Make your changes
6. Write/update tests
7. Update documentation
8. Submit a pull request

## License

See [LICENSE](../LICENSE) file for details.

---

**Need help?** Check the relevant guide above or open an issue on GitHub.
