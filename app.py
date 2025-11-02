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
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8371:AAHWHQCkkDfwAtdV6wVOlCJv17rAZBMpycI")

# User ID that is allowed to send media (will not be deleted)
ALLOWED_USER_ID = 7907871597

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "🤖 Bot is active!\n"
        "I will automatically delete all media messages including photos, videos, stickers, GIFs, and audio. I am desgin by @kingXkingz.\n"
        f"Except for user ID: {ALLOWED_USER_ID}"
    )

async def delete_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete any media message instantly, except for allowed user."""
    try:
        message = update.message
        user_id = message.from_user.id
        chat_id = message.chat_id
        message_id = message.message_id
        
        # Check if user is the allowed user
        if user_id == ALLOWED_USER_ID:
            logger.info(f"Allowed user {user_id} sent media - not deleting")
            return
        
        # Delete the media message for all other users
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Deleted media message {message_id} from user {user_id} in chat {chat_id}")
        
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

    # Start the Bot using polling
    logger.info("Starting bot with polling...")
    logger.info(f"Media deletion disabled for user ID: {ALLOWED_USER_ID}")
    application.run_polling()

if __name__ == '__main__':
    main()
