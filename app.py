import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8582239371:AAHWHQCkkDfwAtdV6wVOlCJv17rAZBMpycI")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "🤖 Bot is active!\n"
        "I will automatically delete all media messages including photos, videos, stickers, GIFs, and audio."
    )

async def delete_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete any media message instantly."""
    try:
        message = update.message
        chat_id = message.chat_id
        message_id = message.message_id
        
        # Delete the media message
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Deleted media message {message_id} from chat {chat_id}")
        
        # Optional: Send a warning message (you can remove this if you don't want it)
        try:
            warning_msg = await message.reply_text("❌ Media messages are not allowed here!")
            # Delete the warning message after 3 seconds
            await asyncio.sleep(3)
            await context.bot.delete_message(chat_id=chat_id, message_id=warning_msg.message_id)
        except Exception as e:
            logger.error(f"Error with warning message: {e}")
            
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by Updates."""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    
    # Add media handler - this will catch all media types
    media_filter = (
        filters.PHOTO | filters.VIDEO | filters.Sticker.ALL | 
        filters.ANIMATION | filters.AUDIO | filters.VOICE |
        filters.Document.ALL
    )
    
    application.add_handler(MessageHandler(media_filter, delete_media))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot using polling (simpler for Heroku)
    logger.info("Starting bot with polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
