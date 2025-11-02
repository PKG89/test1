"""Main entry point for CAD-P Telegram bot."""

import sys
from telegram.ext import Application

from .config import config
from .logging_config import setup_logging, get_logger
from .dependencies import container


logger = get_logger(__name__)


def main():
    """Start the CAD-P bot."""
    # Setup logging
    setup_logging()
    logger.info("Starting CAD-P bot...")
    
    # Validate configuration
    config_errors = config.validate()
    if config_errors:
        logger.error("Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    # Ensure required directories exist
    logger.info("Ensuring required directories exist...")
    config.ensure_directories()
    
    # Initialize services
    logger.info("Initializing services...")
    container.initialize_services()
    
    # Check if we have a bot token
    if not config.BOT_TOKEN:
        logger.error(
            "BOT_TOKEN not set. Please set TELEGRAM_BOT_TOKEN or BOT_TOKEN "
            "environment variable with your bot token from @BotFather"
        )
        sys.exit(1)
    
    # Create application
    logger.info("Creating Telegram application...")
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Add handlers (import here to avoid circular imports)
    try:
        from .bot.handlers import create_conversation_handler
        
        logger.info("Adding conversation handlers...")
        conv_handler = create_conversation_handler()
        application.add_handler(conv_handler)
    except ImportError as e:
        logger.warning(f"Could not import handlers: {e}")
        logger.warning("Bot will start without handlers (placeholder mode)")
    
    # Log startup information
    logger.info("=" * 60)
    logger.info("CAD-P Bot Configuration:")
    logger.info(f"  Log Level: {config.LOG_LEVEL}")
    logger.info(f"  Debug Mode: {config.DEBUG}")
    logger.info(f"  Development Mode: {config.DEVELOPMENT_MODE}")
    logger.info(f"  Max File Size: {config.MAX_FILE_SIZE_MB} MB")
    logger.info(f"  Max Points: {config.MAX_POINTS:,}")
    logger.info(f"  Temp Directory: {config.TEMP_DIR}")
    logger.info(f"  Output Directory: {config.OUTPUT_DIR}")
    logger.info("Feature Flags:")
    logger.info(f"  Densification: {config.ENABLE_DENSIFICATION}")
    logger.info(f"  TIN: {config.ENABLE_TIN}")
    logger.info(f"  Code Catalog: {config.ENABLE_CODE_CATALOG}")
    logger.info(f"  File Validation: {config.ENABLE_FILE_VALIDATION}")
    logger.info(f"  Auto Encoding Detection: {config.ENABLE_AUTO_ENCODING_DETECTION}")
    logger.info("=" * 60)
    
    # Start bot
    logger.info("Starting bot polling...")
    logger.info("Bot is ready to receive messages!")
    
    try:
        application.run_polling(allowed_updates=['message', 'callback_query'])
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
