# Bot Workflow Implementation

## Overview

This implementation provides a complete conversational Telegram bot workflow for processing geospatial data files and generating DXF outputs.

## Features

### Conversational Flow

1. **Start & Greeting** (`/start`)
   - Welcome message with bot capabilities
   - Transition to DXF template confirmation

2. **DXF Template Confirmation**
   - Ask if user has a custom DXF template
   - Store preference for later use

3. **File Upload**
   - Accept .txt/.xyz files
   - Validate file extension and size (max 50MB)
   - Store in temporary workspace
   - Prevent duplicate submissions

4. **Encoding Detection**
   - Automatic detection using chardet library
   - Manual override via inline keyboard
   - Supported: UTF-8, Windows-1251, CP1251, ISO-8859-1

5. **Delimiter Detection**
   - Automatic sniffing of column delimiters
   - Supported: space, tab, comma, semicolon, pipe
   - Manual override option

6. **Data Parsing & Validation**
   - Parse into pandas DataFrame
   - Trim whitespace
   - Coerce coordinates to floats
   - Round Z to 2 decimals
   - Detect anomalies (unusually large values)
   - Log validation errors
   - Surface errors to user

7. **Column Mapping**
   - Default mapping: X Y Z [CODE] [COMMENT]
   - Preview parsed data
   - Option to remap columns (placeholder)

8. **Scale Selection**
   - Choose drawing scale: 1:500, 1:1000, 1:2000, 1:5000

9. **TIN Options**
   - Enable/disable TIN construction
   - Uses existing TIN service

10. **Densification Options**
    - Enable/disable relief densification
    - Uses existing densification service

11. **Confirmation**
    - Show summary of all settings
    - Confirm or cancel

12. **Processing**
    - Stub implementation (ready for integration)
    - Success acknowledgment
    - File cleanup

### Graceful Cancellation

- `/cancel` command available at any time
- Automatic cleanup of uploaded files
- Session data reset

## Architecture

### State Machine

States defined in `src/bot/states.py`:
- `ConversationState` enum with all conversation steps

### Handlers

Async handlers in `src/bot/handlers.py`:
- Each state has dedicated handler functions
- Context-based state storage using `context.user_data`
- Inline keyboards for user choices
- Error handling at each step

### File Processing

`src/bot/file_parser.py` provides:
- `FileParser.detect_encoding()` - chardet-based detection
- `FileParser.detect_delimiter()` - heuristic delimiter detection
- `FileParser.validate_file()` - extension and size checks
- `FileParser.parse_file()` - pandas-based parsing with validation

### Data Models

`src/models/bot_data.py` contains:
- `FileUploadInfo` - uploaded file metadata
- `ColumnMapping` - column index configuration
- `ParsedData` - parsing results and statistics
- `BotSessionData` - complete session state

## Usage

### Starting the Bot

```bash
# Set your bot token
export TELEGRAM_BOT_TOKEN="your-token-here"

# Run the bot
python bot_main.py
```

### Running Tests

```bash
# Run parser tests
pytest tests/test_bot_parser.py -v

# Run state machine tests
pytest tests/test_bot_states.py -v

# Run all bot tests
pytest tests/test_bot*.py -v

# With coverage
pytest tests/test_bot*.py --cov=src.bot --cov-report=html
```

## File Format Support

### Supported Formats

- `.txt` - Text files with space/tab/comma separated values
- `.xyz` - Standard XYZ coordinate files

### Expected Data Format

```
# Comments start with #
X Y Z [CODE] [COMMENT]
100.0 200.0 150.5 1 First point
105.0 205.0 151.2 terrain Ground point
110.0 210.0 152.0 vk Reference marker
```

### Supported Delimiters

- Space (` `)
- Tab (`\t`)
- Comma (`,`)
- Semicolon (`;`)
- Pipe (`|`)

## Integration Points

The bot workflow is designed for integration with existing services:

### TIN Construction
- Uses `src.models.settings.TINSettings`
- Integration with `src.services.tin_service`

### Densification
- Uses `src.models.settings.DensificationSettings`
- Integration with `src.services.densification_service`

### DXF Generation
- Uses `src.models.settings.DXFGenerationSettings`
- Integration with existing DXF processors

### Domain Models
- `SurveyPoint` from `src.models.point_data`
- `ProjectSettings` from `src.models.settings`

## Error Handling

### Validation Errors
- Invalid file extensions
- Oversized files (>50MB)
- Empty files
- Unparseable coordinates
- Insufficient columns

### Recovery Mechanisms
- Retry with different encoding
- Retry with different delimiter
- Re-upload file
- Cancel and restart

### User Feedback
- Clear error messages
- Suggestions for resolution
- Anomaly reporting
- Warning display

## Testing

### Parser Tests (`test_bot_parser.py`)

Coverage includes:
- File validation (extension, size)
- Encoding detection (UTF-8, Windows-1251, etc.)
- Delimiter detection (space, comma, tab, etc.)
- Data parsing (valid/invalid rows)
- Z-coordinate rounding
- Whitespace trimming
- Anomaly detection
- Unicode support
- Edge cases (negative coords, scientific notation)

### State Machine Tests (`test_bot_states.py`)

Coverage includes:
- All state transitions
- Template confirmation flow
- File upload handling
- Encoding/delimiter selection
- Scale selection
- TIN/densification options
- Final confirmation
- Cancellation flows
- Error handling
- Session data management

## Configuration

### File Upload Limits

```python
FileParser.MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
FileParser.SUPPORTED_EXTENSIONS = ['.txt', '.xyz']
```

### Temporary Storage

```python
TEMP_DIR = Path(tempfile.gettempdir()) / "dxf_bot_uploads"
```

Files are automatically cleaned up after processing or cancellation.

## Future Enhancements

1. **Custom Column Mapping UI**
   - Interactive column selection
   - Preview with different mappings

2. **Advanced TIN Options**
   - Breakline configuration
   - Code filtering

3. **Advanced Densification Options**
   - Grid spacing selection
   - Interpolation method choice
   - Layer visibility

4. **Template Upload**
   - Allow users to upload custom DXF templates
   - Template validation

5. **Progress Updates**
   - Real-time processing status
   - Estimated time remaining

6. **Result Preview**
   - Thumbnail generation
   - Statistics display

7. **Batch Processing**
   - Multiple file uploads
   - Queue management

## Dependencies

Required packages:
- `python-telegram-bot>=20.0` - Async Telegram bot framework
- `pandas>=2.0.0` - Data parsing and manipulation
- `chardet>=5.0.0` - Character encoding detection
- `numpy>=1.24.0` - Numerical operations
- `pytest>=7.4.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async test support

## License

Same as parent project.
