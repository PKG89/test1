"""Async conversation handlers for the Telegram bot."""

import logging
import tempfile
from pathlib import Path
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from src.bot.states import ConversationState
from src.bot.file_parser import FileParser, FileParsingError
from src.models.bot_data import (
    BotSessionData,
    FileUploadInfo,
    ColumnMapping
)
from src.models.settings import ProjectSettings, DensificationSettings, TINSettings

logger = logging.getLogger(__name__)


# Temporary directory for file uploads
TEMP_DIR = Path(tempfile.gettempdir()) / "dxf_bot_uploads"
TEMP_DIR.mkdir(exist_ok=True)


def get_session_data(context: ContextTypes.DEFAULT_TYPE) -> BotSessionData:
    """Get or create session data from context."""
    if 'session' not in context.user_data:
        context.user_data['session'] = BotSessionData()
    return context.user_data['session']


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command."""
    user = update.effective_user
    
    # Initialize session data
    get_session_data(context)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "Я помогу вам обработать геодезические данные и создать DXF-файл.\n\n"
        "🔧 **Возможности:**\n"
        "• Импорт файлов .txt/.xyz с координатами\n"
        "• Построение триангуляционной сети (TIN)\n"
        "• Денсификация рельефа\n"
        "• Обработка 60+ кодов съёмки\n"
        "• Генерация DXF-чертежей\n\n"
        "Начнём?\n\n"
        "Используйте /cancel для отмены в любой момент."
    )
    
    return await dxf_template_confirmation(update, context)


async def dxf_template_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask about DXF template usage."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Использовать шаблон", callback_data="template_yes"),
            InlineKeyboardButton("⏭️ Без шаблона", callback_data="template_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "📄 **DXF-шаблон**\n\n"
        "У вас есть готовый DXF-шаблон с настроенными блоками и слоями?\n\n"
        "Если да, система будет использовать его для генерации результата.\n"
        "Если нет, будет создан стандартный DXF-файл."
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    return ConversationState.DXF_TEMPLATE_CONFIRMATION


async def handle_template_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle template choice."""
    query = update.callback_query
    await query.answer()
    
    session = get_session_data(context)
    session.use_template = (query.data == "template_yes")
    
    if session.use_template:
        await query.edit_message_text(
            "✅ Отлично! Система будет использовать ваш DXF-шаблон.\n\n"
            "Теперь загрузите файл с координатами."
        )
    else:
        await query.edit_message_text(
            "✅ Хорошо! Будет создан стандартный DXF-файл.\n\n"
            "Теперь загрузите файл с координатами."
        )
    
    return await request_file_upload(update, context)


async def request_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Request file upload from user."""
    message = (
        "📤 **Загрузка файла**\n\n"
        "Пожалуйста, загрузите файл с координатами.\n\n"
        "**Поддерживаемые форматы:**\n"
        "• .txt (текстовый файл)\n"
        "• .xyz (файл координат)\n\n"
        "**Формат данных:**\n"
        "```\n"
        "X Y Z [CODE] [COMMENT]\n"
        "100.0 200.0 150.5 1 Point description\n"
        "```\n\n"
        "**Ограничения:**\n"
        "• Максимальный размер: 50 МБ\n"
        "• Разделители: пробел, табуляция, запятая\n"
        "• Комментарии начинаются с #"
    )
    
    if update.callback_query:
        query = update.callback_query
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=message
        )
    else:
        await update.message.reply_text(message)
    
    return ConversationState.FILE_UPLOAD


async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle file upload."""
    if not update.message.document:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте файл как документ (не как фото)."
        )
        return ConversationState.FILE_UPLOAD
    
    document = update.message.document
    file_name = document.file_name
    file_size = document.file_size
    
    # Validate file extension
    file_path = TEMP_DIR / f"{update.effective_user.id}_{file_name}"
    
    if file_path.suffix.lower() not in FileParser.SUPPORTED_EXTENSIONS:
        await update.message.reply_text(
            f"❌ Неподдерживаемый формат файла.\n\n"
            f"Поддерживаются: {', '.join(FileParser.SUPPORTED_EXTENSIONS)}"
        )
        return ConversationState.FILE_UPLOAD
    
    # Check size
    if file_size > FileParser.MAX_FILE_SIZE:
        max_mb = FileParser.MAX_FILE_SIZE / (1024 * 1024)
        await update.message.reply_text(
            f"❌ Файл слишком большой.\n\n"
            f"Максимальный размер: {max_mb} МБ"
        )
        return ConversationState.FILE_UPLOAD
    
    # Download file
    try:
        await update.message.reply_text("⏳ Загружаю файл...")
        
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(file_path)
        
        # Validate file
        is_valid, error_msg = FileParser.validate_file(file_path)
        if not is_valid:
            file_path.unlink(missing_ok=True)
            await update.message.reply_text(f"❌ {error_msg}")
            return ConversationState.FILE_UPLOAD
        
        # Store file info
        session = get_session_data(context)
        session.file_info = FileUploadInfo(
            file_path=file_path,
            original_filename=file_name,
            file_size=file_size
        )
        
        await update.message.reply_text(
            f"✅ Файл загружен: {file_name}\n"
            f"📊 Размер: {file_size / 1024:.1f} КБ\n\n"
            "⏳ Определяю кодировку..."
        )
        
        return await detect_encoding(update, context)
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Ошибка при загрузке файла: {str(e)}\n\n"
            "Попробуйте еще раз."
        )
        return ConversationState.FILE_UPLOAD


async def detect_encoding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Detect file encoding."""
    session = get_session_data(context)
    
    try:
        encoding = FileParser.detect_encoding(session.file_info.file_path)
        session.file_info.encoding = encoding
        
        keyboard = [
            [
                InlineKeyboardButton(f"✅ {encoding.upper()}", callback_data=f"encoding_{encoding}"),
                InlineKeyboardButton("🔧 Другая", callback_data="encoding_manual")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🔍 **Определение кодировки**\n\n"
            f"Обнаружена кодировка: **{encoding.upper()}**\n\n"
            f"Всё верно?",
            reply_markup=reply_markup
        )
        
        return ConversationState.ENCODING_DETECTION
        
    except Exception as e:
        logger.error(f"Error detecting encoding: {e}", exc_info=True)
        await update.message.reply_text(
            "⚠️ Не удалось определить кодировку автоматически.\n"
            "Используется UTF-8 по умолчанию."
        )
        session.file_info.encoding = 'utf-8'
        return await detect_delimiter(update, context)


async def handle_encoding_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle encoding choice."""
    query = update.callback_query
    await query.answer()
    
    session = get_session_data(context)
    
    if query.data == "encoding_manual":
        keyboard = [
            [InlineKeyboardButton("UTF-8", callback_data="encoding_utf-8")],
            [InlineKeyboardButton("Windows-1251", callback_data="encoding_windows-1251")],
            [InlineKeyboardButton("CP1251", callback_data="encoding_cp1251")],
            [InlineKeyboardButton("ISO-8859-1", callback_data="encoding_iso-8859-1")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔧 **Выбор кодировки**\n\n"
            "Выберите кодировку файла:",
            reply_markup=reply_markup
        )
        return ConversationState.ENCODING_DETECTION
    else:
        encoding = query.data.replace("encoding_", "")
        session.file_info.encoding = encoding
        
        await query.edit_message_text(
            f"✅ Кодировка: {encoding.upper()}\n\n"
            "⏳ Определяю разделитель..."
        )
        
        return await detect_delimiter(update, context)


async def detect_delimiter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Detect column delimiter."""
    session = get_session_data(context)
    
    try:
        delimiter = FileParser.detect_delimiter(
            session.file_info.file_path,
            session.file_info.encoding
        )
        session.file_info.delimiter = delimiter
        
        delimiter_names = {
            ' ': 'Пробел',
            '\t': 'Табуляция',
            ',': 'Запятая',
            ';': 'Точка с запятой',
            '|': 'Вертикальная черта'
        }
        
        keyboard = [
            [
                InlineKeyboardButton(
                    f"✅ {delimiter_names.get(delimiter, repr(delimiter))}",
                    callback_data=f"delimiter_{ord(delimiter)}"
                ),
                InlineKeyboardButton("🔧 Другой", callback_data="delimiter_manual")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"🔍 **Определение разделителя**\n\n"
            f"Обнаружен разделитель: **{delimiter_names.get(delimiter, repr(delimiter))}**\n\n"
            f"Всё верно?"
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)
        
        return ConversationState.DELIMITER_DETECTION
        
    except Exception as e:
        logger.error(f"Error detecting delimiter: {e}", exc_info=True)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "⚠️ Не удалось определить разделитель.\n"
                "Используется пробел по умолчанию."
            )
        else:
            await update.message.reply_text(
                "⚠️ Не удалось определить разделитель.\n"
                "Используется пробел по умолчанию."
            )
        session.file_info.delimiter = ' '
        return await parse_and_validate(update, context)


async def handle_delimiter_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle delimiter choice."""
    query = update.callback_query
    await query.answer()
    
    session = get_session_data(context)
    
    if query.data == "delimiter_manual":
        keyboard = [
            [InlineKeyboardButton("Пробел", callback_data=f"delimiter_{ord(' ')}")],
            [InlineKeyboardButton("Табуляция", callback_data=f"delimiter_{ord('\t')}")],
            [InlineKeyboardButton("Запятая", callback_data=f"delimiter_{ord(',')}")],
            [InlineKeyboardButton("Точка с запятой", callback_data=f"delimiter_{ord(';')}")],
            [InlineKeyboardButton("Вертикальная черта", callback_data=f"delimiter_{ord('|')}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔧 **Выбор разделителя**\n\n"
            "Выберите разделитель столбцов:",
            reply_markup=reply_markup
        )
        return ConversationState.DELIMITER_DETECTION
    else:
        delimiter_code = int(query.data.replace("delimiter_", ""))
        delimiter = chr(delimiter_code)
        session.file_info.delimiter = delimiter
        
        await query.edit_message_text(
            f"✅ Разделитель выбран\n\n"
            "⏳ Парсю файл..."
        )
        
        return await parse_and_validate(update, context)


async def parse_and_validate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parse file and validate data."""
    session = get_session_data(context)
    
    try:
        # Parse file with default column mapping
        parsed_data = FileParser.parse_file(
            session.file_info.file_path,
            session.file_info.encoding,
            session.file_info.delimiter,
            session.column_mapping
        )
        
        session.parsed_data = parsed_data
        
        # Build summary message
        message = (
            f"✅ **Файл успешно обработан**\n\n"
            f"📊 **Статистика:**\n"
            f"• Всего строк: {parsed_data.total_rows}\n"
            f"• Валидных точек: {parsed_data.valid_rows}\n"
            f"• Невалидных строк: {parsed_data.invalid_rows}\n"
        )
        
        if parsed_data.anomalies:
            message += f"\n⚠️ **Обнаружено аномалий:** {len(parsed_data.anomalies)}\n"
            for anomaly in parsed_data.anomalies[:3]:
                message += f"• {anomaly}\n"
        
        if parsed_data.warnings:
            message += f"\n⚠️ **Предупреждения:** {len(parsed_data.warnings)}\n"
            for warning in parsed_data.warnings[:3]:
                message += f"• {warning}\n"
        
        # Sample points
        sample_points = parsed_data.points[:3]
        if sample_points:
            message += "\n📍 **Образец данных:**\n"
            for point in sample_points:
                code = point.get('code', '—')
                message += f"• X={point['x']:.2f}, Y={point['y']:.2f}, Z={point['z']:.2f}, Code={code}\n"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Продолжить", callback_data="parse_continue"),
                InlineKeyboardButton("🔧 Изменить маппинг", callback_data="parse_remap")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)
        
        return ConversationState.COLUMN_MAPPING
        
    except FileParsingError as e:
        error_message = (
            f"❌ **Ошибка парсинга файла**\n\n"
            f"{str(e)}\n\n"
            "Попробуйте изменить параметры или загрузить другой файл."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔧 Изменить параметры", callback_data="parse_retry")],
            [InlineKeyboardButton("📤 Загрузить другой файл", callback_data="parse_reupload")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(error_message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(error_message, reply_markup=reply_markup)
        
        return ConversationState.COLUMN_MAPPING


async def handle_parse_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle parse confirmation."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "parse_continue":
        await query.edit_message_text(
            "✅ Отлично! Данные готовы к обработке.\n\n"
            "Теперь настроим параметры генерации."
        )
        return await request_scale(update, context)
    elif query.data == "parse_remap":
        await query.edit_message_text(
            "🔧 Изменение маппинга столбцов пока не реализовано.\n"
            "Используется стандартное: X Y Z [CODE] [COMMENT]"
        )
        return await request_scale(update, context)
    elif query.data == "parse_retry":
        return await detect_encoding(update, context)
    elif query.data == "parse_reupload":
        return await request_file_upload(update, context)


async def request_scale(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Request drawing scale."""
    keyboard = [
        [InlineKeyboardButton("1:500", callback_data="scale_500")],
        [InlineKeyboardButton("1:1000", callback_data="scale_1000")],
        [InlineKeyboardButton("1:2000", callback_data="scale_2000")],
        [InlineKeyboardButton("1:5000", callback_data="scale_5000")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "📐 **Масштаб чертежа**\n\n"
        "Выберите масштаб для генерации DXF:"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup
        )
    
    return ConversationState.SCALE_SELECTION


async def handle_scale_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle scale choice."""
    query = update.callback_query
    await query.answer()
    
    session = get_session_data(context)
    scale_str = query.data.replace("scale_", "")
    session.scale = float(scale_str)
    
    await query.edit_message_text(
        f"✅ Масштаб: 1:{scale_str}\n\n"
        "Теперь настроим построение TIN."
    )
    
    return await request_tin_options(update, context)


async def request_tin_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Request TIN options."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Включить TIN", callback_data="tin_yes"),
            InlineKeyboardButton("⏭️ Пропустить", callback_data="tin_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "🔺 **Построение TIN**\n\n"
        "TIN (Triangulated Irregular Network) - триангуляционная сеть для моделирования поверхности.\n\n"
        "Построить TIN?"
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )
    
    return ConversationState.TIN_OPTIONS


async def handle_tin_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle TIN choice."""
    query = update.callback_query
    await query.answer()
    
    session = get_session_data(context)
    session.tin_enabled = (query.data == "tin_yes")
    
    if session.tin_enabled:
        await query.edit_message_text(
            "✅ TIN будет построен\n\n"
            "Теперь настроим денсификацию."
        )
    else:
        await query.edit_message_text(
            "⏭️ TIN пропущен\n\n"
            "Теперь настроим денсификацию."
        )
    
    return await request_densification_options(update, context)


async def request_densification_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Request densification options."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Включить денсификацию", callback_data="densify_yes"),
            InlineKeyboardButton("⏭️ Пропустить", callback_data="densify_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "🎯 **Денсификация рельефа**\n\n"
        "Денсификация автоматически добавляет точки в разреженных областях "
        "для улучшения детализации поверхности.\n\n"
        "Включить денсификацию?"
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )
    
    return ConversationState.DENSIFICATION_OPTIONS


async def handle_densification_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle densification choice."""
    query = update.callback_query
    await query.answer()
    
    session = get_session_data(context)
    session.densification_enabled = (query.data == "densify_yes")
    
    if session.densification_enabled:
        await query.edit_message_text(
            "✅ Денсификация будет выполнена\n\n"
            "Переходим к подтверждению."
        )
    else:
        await query.edit_message_text(
            "⏭️ Денсификация пропущена\n\n"
            "Переходим к подтверждению."
        )
    
    return await show_confirmation(update, context)


async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show final confirmation."""
    session = get_session_data(context)
    
    message = (
        "📋 **Итоговые настройки**\n\n"
        f"📄 Файл: {session.file_info.original_filename}\n"
        f"📊 Точек: {session.parsed_data.valid_rows}\n"
        f"📐 Масштаб: 1:{int(session.scale)}\n"
        f"🔺 TIN: {'✅ Да' if session.tin_enabled else '⏭️ Нет'}\n"
        f"🎯 Денсификация: {'✅ Да' if session.densification_enabled else '⏭️ Нет'}\n"
        f"📄 Шаблон: {'✅ Да' if session.use_template else '⏭️ Нет'}\n\n"
        "Всё верно? Начинаем обработку?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Начать обработку", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Отменить", callback_data="confirm_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )
    
    return ConversationState.CONFIRMATION


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle final confirmation."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_cancel":
        await query.edit_message_text(
            "❌ Обработка отменена.\n\n"
            "Используйте /start для начала заново."
        )
        return ConversationHandler.END
    
    await query.edit_message_text(
        "🚀 **Начинаю обработку...**\n\n"
        "⏳ Пожалуйста, подождите. Это может занять некоторое время."
    )
    
    return await process_data(update, context)


async def process_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process data (stub implementation)."""
    session = get_session_data(context)
    
    try:
        # This is a stub - actual processing would integrate with existing services
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "✅ **Обработка завершена успешно!**\n\n"
                f"📊 **Результаты:**\n"
                f"• Обработано точек: {session.parsed_data.valid_rows}\n"
                f"• TIN: {'✅ Построен' if session.tin_enabled else '⏭️ Пропущен'}\n"
                f"• Денсификация: {'✅ Выполнена' if session.densification_enabled else '⏭️ Пропущена'}\n\n"
                "🎉 DXF-файл готов!\n\n"
                "_(Это заглушка. Реальная интеграция с processing service будет добавлена позже)_\n\n"
                "Используйте /start для новой обработки."
            )
        )
        
        # Cleanup
        if session.file_info and session.file_info.file_path.exists():
            session.file_info.file_path.unlink(missing_ok=True)
        
        session.reset()
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"❌ **Ошибка при обработке**\n\n"
                f"{str(e)}\n\n"
                "Попробуйте еще раз или обратитесь в поддержку."
            )
        )
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation."""
    session = get_session_data(context)
    
    # Cleanup uploaded file
    if session.file_info and session.file_info.file_path.exists():
        session.file_info.file_path.unlink(missing_ok=True)
    
    session.reset()
    
    await update.message.reply_text(
        "❌ Обработка отменена.\n\n"
        "Используйте /start для начала заново."
    )
    
    return ConversationHandler.END


def create_conversation_handler() -> ConversationHandler:
    """Create and return the conversation handler."""
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ConversationState.DXF_TEMPLATE_CONFIRMATION: [
                CallbackQueryHandler(handle_template_choice, pattern='^template_')
            ],
            ConversationState.FILE_UPLOAD: [
                MessageHandler(filters.Document.ALL, handle_file_upload)
            ],
            ConversationState.ENCODING_DETECTION: [
                CallbackQueryHandler(handle_encoding_choice, pattern='^encoding_')
            ],
            ConversationState.DELIMITER_DETECTION: [
                CallbackQueryHandler(handle_delimiter_choice, pattern='^delimiter_')
            ],
            ConversationState.COLUMN_MAPPING: [
                CallbackQueryHandler(handle_parse_confirmation, pattern='^parse_')
            ],
            ConversationState.SCALE_SELECTION: [
                CallbackQueryHandler(handle_scale_choice, pattern='^scale_')
            ],
            ConversationState.TIN_OPTIONS: [
                CallbackQueryHandler(handle_tin_choice, pattern='^tin_')
            ],
            ConversationState.DENSIFICATION_OPTIONS: [
                CallbackQueryHandler(handle_densification_choice, pattern='^densify_')
            ],
            ConversationState.CONFIRMATION: [
                CallbackQueryHandler(handle_confirmation, pattern='^confirm_')
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        name="main_conversation",
        persistent=False
    )
