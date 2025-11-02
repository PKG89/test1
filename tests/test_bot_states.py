"""Tests for bot conversation state machine."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User, Message, Document, Chat, CallbackQuery
from telegram.ext import ContextTypes

from src.bot.states import ConversationState
from src.bot.handlers import (
    start,
    handle_template_choice,
    handle_file_upload,
    handle_encoding_choice,
    handle_delimiter_choice,
    handle_parse_confirmation,
    handle_scale_choice,
    handle_tin_choice,
    handle_densification_choice,
    handle_confirmation,
    cancel
)
from src.models.bot_data import BotSessionData


@pytest.fixture
def mock_update():
    """Create mock Update object."""
    update = MagicMock(spec=Update)
    update.effective_user = User(id=123, first_name="Test", is_bot=False)
    update.effective_chat = Chat(id=123, type='private')
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    update.callback_query = None
    return update


@pytest.fixture
def mock_context():
    """Create mock Context object."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    context.bot = MagicMock()
    context.bot.get_file = AsyncMock()
    context.bot.send_message = AsyncMock()
    return context


@pytest.fixture
def mock_callback_query_update(mock_update):
    """Create mock Update with CallbackQuery."""
    update = mock_update
    update.callback_query = MagicMock(spec=CallbackQuery)
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    update.callback_query.message = update.message
    return update


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample test file."""
    file_path = tmp_path / "test_data.txt"
    content = """100.0 200.0 150.5 1 First point
105.0 205.0 151.2 2 Second point
110.0 210.0 152.0 3 Third point
"""
    file_path.write_text(content, encoding='utf-8')
    return file_path


class TestStartState:
    """Test /start command and initial state."""
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_update, mock_context):
        """Test /start command initiates conversation."""
        result = await start(mock_update, mock_context)
        
        # Should transition to DXF_TEMPLATE_CONFIRMATION
        assert result == ConversationState.DXF_TEMPLATE_CONFIRMATION
        
        # Should send two messages: welcome + template confirmation
        # The last message should be about DXF template
        assert mock_update.message.reply_text.called
        # Check that at least one call was made
        assert mock_update.message.reply_text.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_session_data_initialized(self, mock_update, mock_context):
        """Test that session data is initialized."""
        await start(mock_update, mock_context)
        
        assert 'session' in mock_context.user_data
        session = mock_context.user_data['session']
        assert isinstance(session, BotSessionData)


class TestTemplateConfirmation:
    """Test DXF template confirmation state."""
    
    @pytest.mark.asyncio
    async def test_template_yes(self, mock_callback_query_update, mock_context):
        """Test choosing to use template."""
        mock_callback_query_update.callback_query.data = "template_yes"
        
        result = await handle_template_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.FILE_UPLOAD
        assert mock_callback_query_update.callback_query.answer.called
        
        session = mock_context.user_data['session']
        assert session.use_template is True
    
    @pytest.mark.asyncio
    async def test_template_no(self, mock_callback_query_update, mock_context):
        """Test choosing not to use template."""
        mock_callback_query_update.callback_query.data = "template_no"
        
        result = await handle_template_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.FILE_UPLOAD
        
        session = mock_context.user_data['session']
        assert session.use_template is False


class TestFileUpload:
    """Test file upload state."""
    
    @pytest.mark.asyncio
    async def test_valid_file_upload(self, mock_update, mock_context, sample_file):
        """Test uploading a valid file."""
        # Setup document
        mock_update.message.document = MagicMock(spec=Document)
        mock_update.message.document.file_name = "test_data.txt"
        mock_update.message.document.file_size = 1024
        mock_update.message.document.file_id = "file123"
        
        # Mock file download
        mock_file = MagicMock()
        mock_file.download_to_drive = AsyncMock()
        mock_context.bot.get_file.return_value = mock_file
        
        with patch('src.bot.handlers.FileParser.validate_file', return_value=(True, "")):
            with patch('src.bot.handlers.FileParser.detect_encoding', return_value='utf-8'):
                result = await handle_file_upload(mock_update, mock_context)
        
        assert result == ConversationState.ENCODING_DETECTION
        assert mock_context.bot.get_file.called
        
        session = mock_context.user_data['session']
        assert session.file_info is not None
        assert session.file_info.original_filename == "test_data.txt"
    
    @pytest.mark.asyncio
    async def test_invalid_extension(self, mock_update, mock_context):
        """Test rejection of invalid file extension."""
        mock_update.message.document = MagicMock(spec=Document)
        mock_update.message.document.file_name = "test_data.doc"
        mock_update.message.document.file_size = 1024
        
        result = await handle_file_upload(mock_update, mock_context)
        
        # Should stay in FILE_UPLOAD state
        assert result == ConversationState.FILE_UPLOAD
        
        # Should send error message
        assert mock_update.message.reply_text.called
        call_args = mock_update.message.reply_text.call_args
        assert "Неподдерживаемый" in call_args[0][0] or "Unsupported" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_oversized_file(self, mock_update, mock_context):
        """Test rejection of oversized file."""
        mock_update.message.document = MagicMock(spec=Document)
        mock_update.message.document.file_name = "test_data.txt"
        mock_update.message.document.file_size = 100 * 1024 * 1024  # 100MB
        
        result = await handle_file_upload(mock_update, mock_context)
        
        assert result == ConversationState.FILE_UPLOAD
        assert mock_update.message.reply_text.called


class TestEncodingDetection:
    """Test encoding detection state."""
    
    @pytest.mark.asyncio
    async def test_accept_detected_encoding(self, mock_callback_query_update, mock_context):
        """Test accepting detected encoding."""
        # Setup session with file info
        session = BotSessionData()
        session.file_info = MagicMock()
        session.file_info.file_path = Path("/tmp/test.txt")
        session.file_info.encoding = 'utf-8'
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "encoding_utf-8"
        
        with patch('src.bot.handlers.FileParser.detect_delimiter', return_value=' '):
            result = await handle_encoding_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.DELIMITER_DETECTION
        assert session.file_info.encoding == 'utf-8'
    
    @pytest.mark.asyncio
    async def test_manual_encoding_selection(self, mock_callback_query_update, mock_context):
        """Test manual encoding selection."""
        session = BotSessionData()
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "encoding_manual"
        
        result = await handle_encoding_choice(mock_callback_query_update, mock_context)
        
        # Should stay in ENCODING_DETECTION to show options
        assert result == ConversationState.ENCODING_DETECTION
        assert mock_callback_query_update.callback_query.edit_message_text.called


class TestDelimiterDetection:
    """Test delimiter detection state."""
    
    @pytest.mark.asyncio
    async def test_accept_detected_delimiter(self, mock_callback_query_update, mock_context, sample_file):
        """Test accepting detected delimiter."""
        session = BotSessionData()
        session.file_info = MagicMock()
        session.file_info.file_path = sample_file
        session.file_info.encoding = 'utf-8'
        session.file_info.delimiter = ' '
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = f"delimiter_{ord(' ')}"
        
        with patch('src.bot.handlers.FileParser.parse_file') as mock_parse:
            mock_parse.return_value = MagicMock(
                total_rows=3,
                valid_rows=3,
                invalid_rows=0,
                points=[
                    {'x': 100.0, 'y': 200.0, 'z': 150.5, 'code': '1'},
                    {'x': 105.0, 'y': 205.0, 'z': 151.2, 'code': '2'},
                    {'x': 110.0, 'y': 210.0, 'z': 152.0, 'code': '3'}
                ],
                anomalies=[],
                warnings=[]
            )
            
            result = await handle_delimiter_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.COLUMN_MAPPING
        assert session.file_info.delimiter == ' '
    
    @pytest.mark.asyncio
    async def test_manual_delimiter_selection(self, mock_callback_query_update, mock_context):
        """Test manual delimiter selection."""
        session = BotSessionData()
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "delimiter_manual"
        
        result = await handle_delimiter_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.DELIMITER_DETECTION
        assert mock_callback_query_update.callback_query.edit_message_text.called


class TestParseConfirmation:
    """Test parse confirmation state."""
    
    @pytest.mark.asyncio
    async def test_continue_after_parse(self, mock_callback_query_update, mock_context):
        """Test continuing after successful parse."""
        session = BotSessionData()
        session.parsed_data = MagicMock()
        session.parsed_data.valid_rows = 10
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "parse_continue"
        
        result = await handle_parse_confirmation(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.SCALE_SELECTION
    
    @pytest.mark.asyncio
    async def test_remap_columns(self, mock_callback_query_update, mock_context):
        """Test remapping columns."""
        session = BotSessionData()
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "parse_remap"
        
        result = await handle_parse_confirmation(mock_callback_query_update, mock_context)
        
        # Currently goes to scale selection as remapping is not fully implemented
        assert result == ConversationState.SCALE_SELECTION


class TestScaleSelection:
    """Test scale selection state."""
    
    @pytest.mark.asyncio
    async def test_scale_1000(self, mock_callback_query_update, mock_context):
        """Test selecting 1:1000 scale."""
        session = BotSessionData()
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "scale_1000"
        
        result = await handle_scale_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.TIN_OPTIONS
        assert session.scale == 1000.0
    
    @pytest.mark.asyncio
    async def test_scale_500(self, mock_callback_query_update, mock_context):
        """Test selecting 1:500 scale."""
        session = BotSessionData()
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "scale_500"
        
        result = await handle_scale_choice(mock_callback_query_update, mock_context)
        
        assert session.scale == 500.0


class TestTINOptions:
    """Test TIN options state."""
    
    @pytest.mark.asyncio
    async def test_enable_tin(self, mock_callback_query_update, mock_context):
        """Test enabling TIN."""
        session = BotSessionData()
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "tin_yes"
        
        result = await handle_tin_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.DENSIFICATION_OPTIONS
        assert session.tin_enabled is True
    
    @pytest.mark.asyncio
    async def test_disable_tin(self, mock_callback_query_update, mock_context):
        """Test disabling TIN."""
        session = BotSessionData()
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "tin_no"
        
        result = await handle_tin_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.DENSIFICATION_OPTIONS
        assert session.tin_enabled is False


class TestDensificationOptions:
    """Test densification options state."""
    
    @pytest.mark.asyncio
    async def test_enable_densification(self, mock_callback_query_update, mock_context):
        """Test enabling densification."""
        session = BotSessionData()
        session.file_info = MagicMock()
        session.file_info.original_filename = "test.txt"
        session.parsed_data = MagicMock()
        session.parsed_data.valid_rows = 10
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "densify_yes"
        
        result = await handle_densification_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.CONFIRMATION
        assert session.densification_enabled is True
    
    @pytest.mark.asyncio
    async def test_disable_densification(self, mock_callback_query_update, mock_context):
        """Test disabling densification."""
        session = BotSessionData()
        session.file_info = MagicMock()
        session.file_info.original_filename = "test.txt"
        session.parsed_data = MagicMock()
        session.parsed_data.valid_rows = 10
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "densify_no"
        
        result = await handle_densification_choice(mock_callback_query_update, mock_context)
        
        assert result == ConversationState.CONFIRMATION
        assert session.densification_enabled is False


class TestConfirmation:
    """Test final confirmation state."""
    
    @pytest.mark.asyncio
    async def test_confirm_and_process(self, mock_callback_query_update, mock_context):
        """Test confirming and starting processing."""
        session = BotSessionData()
        session.file_info = MagicMock()
        session.file_info.original_filename = "test.txt"
        session.file_info.file_path = MagicMock()
        session.file_info.file_path.exists.return_value = False
        session.parsed_data = MagicMock()
        session.parsed_data.valid_rows = 10
        session.scale = 1000.0
        session.tin_enabled = True
        session.densification_enabled = False
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "confirm_yes"
        
        from telegram.ext import ConversationHandler
        result = await handle_confirmation(mock_callback_query_update, mock_context)
        
        # Should end conversation after processing
        assert result == ConversationHandler.END
    
    @pytest.mark.asyncio
    async def test_cancel_at_confirmation(self, mock_callback_query_update, mock_context):
        """Test canceling at confirmation stage."""
        session = BotSessionData()
        mock_context.user_data['session'] = session
        
        mock_callback_query_update.callback_query.data = "confirm_cancel"
        
        from telegram.ext import ConversationHandler
        result = await handle_confirmation(mock_callback_query_update, mock_context)
        
        assert result == ConversationHandler.END


class TestCancellation:
    """Test conversation cancellation."""
    
    @pytest.mark.asyncio
    async def test_cancel_command(self, mock_update, mock_context):
        """Test /cancel command."""
        session = BotSessionData()
        session.file_info = MagicMock()
        session.file_info.file_path = MagicMock()
        session.file_info.file_path.exists.return_value = False
        mock_context.user_data['session'] = session
        
        from telegram.ext import ConversationHandler
        result = await cancel(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        assert mock_update.message.reply_text.called
    
    @pytest.mark.asyncio
    async def test_cancel_cleans_up_file(self, mock_update, mock_context, tmp_path):
        """Test that cancel cleans up uploaded file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        session = BotSessionData()
        session.file_info = MagicMock()
        session.file_info.file_path = test_file
        mock_context.user_data['session'] = session
        
        await cancel(mock_update, mock_context)
        
        # File should be deleted
        assert not test_file.exists()


class TestSessionDataReset:
    """Test session data reset functionality."""
    
    def test_session_reset(self):
        """Test that session reset clears all data."""
        session = BotSessionData()
        session.file_info = MagicMock()
        session.scale = 2000.0
        session.tin_enabled = False
        session.densification_enabled = True
        
        session.reset()
        
        assert session.file_info is None
        assert session.scale == 1.0
        assert session.tin_enabled is True
        assert session.densification_enabled is False


class TestErrorHandling:
    """Test error handling in various states."""
    
    @pytest.mark.asyncio
    async def test_file_upload_error(self, mock_update, mock_context):
        """Test handling of file upload errors."""
        mock_update.message.document = MagicMock(spec=Document)
        mock_update.message.document.file_name = "test_data.txt"
        mock_update.message.document.file_size = 1024
        mock_update.message.document.file_id = "file123"
        
        # Mock download to raise exception
        mock_context.bot.get_file.side_effect = Exception("Network error")
        
        result = await handle_file_upload(mock_update, mock_context)
        
        # Should stay in FILE_UPLOAD state
        assert result == ConversationState.FILE_UPLOAD
        
        # Should send error message
        assert mock_update.message.reply_text.called
        call_args = mock_update.message.reply_text.call_args
        assert "Ошибка" in call_args[0][0] or "Error" in call_args[0][0]
