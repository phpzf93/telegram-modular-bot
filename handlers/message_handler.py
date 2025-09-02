from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import log_message
from database import UserDatabase
import logging

logger = logging.getLogger(__name__)
db = UserDatabase()

class MessageHandler:
    """Handle regular user messages"""
    
    @staticmethod
    @log_message
    async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        user = update.effective_user
        message_text = update.message.text
        
        # Add user to database
        db.add_user(user.id, user.username, user.first_name)
        
        # Echo the message back with user info
        response = f"👋 Hello {user.first_name}!\n\n"
        response += f"📝 You said: {message_text}\n"
        response += f"🆔 Your ID: {user.id}\n"
        response += f"👤 Username: @{user.username or 'Not set'}\n\n"
        response += f"💰 Your wallet balance: ${db.get_wallet_balance(user.id):.2f}"
        
        await update.message.reply_text(response)
    
    @staticmethod
    @log_message
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming photos"""
        user = update.effective_user
        photo = update.message.photo[-1]  # Get the largest photo
        
        # Add user to database
        db.add_user(user.id, user.username, user.first_name)
        
        response = f"📸 Photo received from {user.first_name}!\n"
        response += f"🆔 File ID: {photo.file_id}\n"
        response += f"📏 Size: {photo.width}x{photo.height}"
        
        await update.message.reply_text(response)
    
    @staticmethod
    @log_message
    async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming documents"""
        user = update.effective_user
        document = update.message.document
        
        # Add user to database
        db.add_user(user.id, user.username, user.first_name)
        
        response = f"📄 Document received from {user.first_name}!\n"
        response += f"📝 Filename: {document.file_name}\n"
        response += f"📊 Size: {document.file_size} bytes\n"
        response += f"🆔 File ID: {document.file_id}"
        
        await update.message.reply_text(response)
    
    @staticmethod
    @log_message
    async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Add user to database
        db.add_user(user.id, user.username, user.first_name)
        
        welcome_message = f"🤖 Welcome to the Modular Bot, {user.first_name}!\n\n"
        welcome_message += "📋 **Available commands:**\n"
        welcome_message += "• /start - Show this welcome message\n"
        welcome_message += "• /help - Get help information\n"
        welcome_message += "• /info - Get your user information\n\n"
        welcome_message += "💰 **Wallet commands:**\n"
        welcome_message += "• /wallet - Check your wallet balance\n"
        welcome_message += "• /wallet_history - View transaction history\n"
        welcome_message += "• /wallet_deposit <amount> - Demo deposit\n"
        welcome_message += "• /wallet_withdraw <amount> - Demo withdrawal\n\n"
        welcome_message += "💬 Send me any message and I'll echo it back!\n"
        welcome_message += "📸 You can also send photos and documents."
        
        await update.message.reply_text(welcome_message)
    
    @staticmethod
    @log_message
    async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        
        help_message = "🆘 **Bot Help**\n\n"
        help_message += "This is a modular Telegram bot that can:\n"
        help_message += "• 💬 Receive and respond to your messages\n"
        help_message += "• 📸 Handle photos and documents\n"
        help_message += "• 💰 Manage your digital wallet\n"
        help_message += "• 🔧 Provide admin functions (for authorized users)\n\n"
        help_message += "📋 **User Commands:**\n"
        help_message += "• `/start` - Welcome message\n"
        help_message += "• `/help` - This help message\n"
        help_message += "• `/info` - Your user information\n\n"
        help_message += "💰 **Wallet Commands:**\n"
        help_message += "• `/wallet` - Check balance\n"
        help_message += "• `/wallet_history` - Transaction history\n"
        help_message += "• `/wallet_deposit <amount>` - Demo deposit\n"
        help_message += "• `/wallet_withdraw <amount>` - Demo withdrawal\n\n"
        help_message += "🤖 Just send me any message to get started!"
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    @staticmethod
    @log_message
    async def handle_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /info command"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        
        user_data = db.get_user(user.id)
        wallet_balance = db.get_wallet_balance(user.id)
        
        info_message = f"👤 **Your Information:**\n\n"
        info_message += f"🆔 User ID: `{user.id}`\n"
        info_message += f"👤 First Name: {user.first_name}\n"
        info_message += f"👤 Last Name: {user.last_name or 'Not set'}\n"
        info_message += f"📧 Username: @{user.username or 'Not set'}\n"
        info_message += f"🌐 Language: {user.language_code or 'Not set'}\n"
        info_message += f"💰 Wallet Balance: ${wallet_balance:.2f}\n"
        if user_data:
            info_message += f"📅 Joined: {user_data['joined_date'][:10]}"
        
        await update.message.reply_text(info_message, parse_mode='Markdown')