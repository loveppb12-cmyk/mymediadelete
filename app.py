import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8582239371:AAHWHQCkkDfwAtdV6wVOlCJv17rAZBMpycI"
API_ID = 20284828
API_HASH = "a980ba25306901d5c9b899414d6a9ab7"

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
        
        # List of media types to delete
        media_types = [
            filters.PHOTO, filters.VIDEO, filters.STICKER, 
            filters.Animation.ALL, filters.AUDIO, filters.VOICE,
            filters.Document.ALL
        ]
        
        # Check if the message contains any media
        is_media = any(
            await media_type.check_update(update) 
            for media_type in media_types
        )
        
        if is_media:
            # Delete the media message
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info(f"Deleted media message {message_id} from chat {chat_id}")
            
            # Optional: Send a warning message (you can remove this if you don't want it)
            warning_msg = await message.reply_text("❌ Media messages are not allowed here!")
            
            # Delete the warning message after 3 seconds
            await context.bot.delete_message(
                chat_id=chat_id, 
                message_id=warning_msg.message_id, 
                delay=3
            )
            
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
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.STICKER | 
        filters.Animation.ALL | filters.AUDIO | filters.VOICE |
        filters.Document.ALL,
        delete_media
    ))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    if os.environ.get('DYNO'):  # Running on Heroku
        port = int(os.environ.get('PORT', 8443))
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=f"https://your-app-name.herokuapp.com/{BOT_TOKEN}"
        )
    else:  # Running locally
        application.run_polling()

if __name__ == '__main__':
    main()
