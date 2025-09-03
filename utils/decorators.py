from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from bot_config import BotConfig
import logging

logger = logging.getLogger(__name__)

def admin_required(func):
    """Decorator to restrict access to admin users only"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        if not BotConfig.is_admin(user_id):
            logger.warning(f"Unauthorized admin access attempt by user {username} (ID: {user_id})")
            await update.message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        logger.info(f"Admin command executed by {username} (ID: {user_id})")
        return await func(update, context)
    
    return wrapper

def log_message(func):
    """Decorator to log incoming messages"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        message_text = update.message.text or "[Non-text message]"
        
        logger.info(f"Message from {username} (ID: {user_id}): {message_text}")
        return await func(update, context)
    
    return wrapper