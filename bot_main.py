"""Main entry point for the Telegram bot."""

import os
import logging
from telegram.ext import Application
from src.bot.handlers import create_conversation_handler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot."""
    # Get token from environment
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN environment variable not set.\n"
            "Please set it with your bot token from @BotFather"
        )
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add conversation handler
    conv_handler = create_conversation_handler()
    application.add_handler(conv_handler)
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=['message', 'callback_query'])


if __name__ == '__main__':
    main()
