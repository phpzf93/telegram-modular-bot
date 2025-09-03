from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import log_message
from database import UserDatabase
import logging

logger = logging.getLogger(__name__)
db = UserDatabase()

class MessageHandler:
    FEE_PERCENT = 0.02  # 2% fee
    @staticmethod
    async def handle_topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        from telegram import ReplyKeyboardMarkup
        user = update.effective_user
        keyboard = [["QRPH"], ["Payment Link"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("How would you like to pay? Choose QRPH or Payment Link:", reply_markup=reply_markup)
        context.user_data['topup_method_pending'] = True
    @staticmethod
    async def handle_topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        from utils.xendit_api import create_invoice
        user = update.effective_user
        await update.message.reply_text("💳 Please enter the amount to top up (minimum 100P):")
        context.user_data['topup_pending'] = True

    @staticmethod
    async def handle_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text("🏧 Please enter the amount to withdraw (minimum 1000P):")
        context.user_data['withdraw_pending'] = True
    """Handle regular user messages"""
    
    @staticmethod
    @log_message
    async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Handle topup method selection
        if context.user_data.get('topup_method_pending'):
            method = message_text.strip().lower()
            if method not in ["qrph", "payment link"]:
                await update.message.reply_text("❌ Please choose either QRPH or Payment Link.")
                return
            context.user_data['topup_method'] = method
            context.user_data['topup_method_pending'] = False
            await update.message.reply_text("💳 Please enter the amount to top up (minimum 100P):")
            context.user_data['topup_pending'] = True
            return
        # Handle pending topup
        if context.user_data.get('topup_pending'):
            try:
                amount = int(message_text)
            except ValueError:
                await update.message.reply_text("❌ Please enter a valid number for top up.")
                return
            if amount < 100:
                await update.message.reply_text("❌ Minimum top up is 100P.")
                return
            fee = int(amount * MessageHandler.FEE_PERCENT)
            net_amount = amount - fee
            from utils.xendit_api import create_invoice
            invoice = await create_invoice(amount, user.id)
            method = context.user_data.get('topup_method', 'payment link')
            fee_msg = f"A {MessageHandler.FEE_PERCENT*100:.0f}% fee ({fee}P) will be deducted. You will receive {net_amount}P in your wallet after payment."
            if method == "qrph":
                qr_url = invoice.get('qr_code_url') or invoice.get('qr_code')
                if qr_url:
                    await context.bot.send_photo(
                        chat_id=user.id,
                        photo=qr_url,
                        caption=f"Scan this QRPH code to pay via Xendit.\n{fee_msg}"
                    )
                else:
                    await update.message.reply_text("❌ QRPH code not available. Please try payment link instead.")
            else:
                if 'invoice_url' in invoice:
                    await update.message.reply_text(f"✅ Top up invoice created! Please pay using this link: {invoice['invoice_url']}\n{fee_msg}")
                else:
                    await update.message.reply_text("❌ Failed to create invoice. Please try again later.")
            context.user_data['topup_pending'] = False
            context.user_data['topup_method'] = None
            return
        # Handle pending withdraw
        if context.user_data.get('withdraw_pending'):
            try:
                amount = int(message_text)
            except ValueError:
                await update.message.reply_text("❌ Please enter a valid number for withdrawal.")
                return
            if amount < 1000:
                await update.message.reply_text("❌ Minimum withdrawal is 1000P.")
                return
            fee = int(amount * MessageHandler.FEE_PERCENT)
            net_amount = amount - fee
            from utils.xendit_api import create_withdrawal
            withdraw_result = await create_withdrawal(net_amount, user.id)
            await update.message.reply_text(f"✅ Withdrawal request received! {amount}P requested, {fee}P fee deducted, {net_amount}P will be sent. Status: {withdraw_result['status']}")
            context.user_data['withdraw_pending'] = False
            return
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
        
        # If user is admin, check if replying to a forwarded message
        from bot_config import BotConfig
        if BotConfig.is_admin(user.id) and update.message.reply_to_message:
            # Try to extract original user ID from the forwarded message
            if update.message.reply_to_message.forward_sender_name:
                # Not available for bots, fallback to context
                await update.message.reply_text("Cannot identify original user from forwarded message.")
                return
            # Try to get user_id from reply_to_message metadata
            orig_user_id = update.message.reply_to_message.caption
            if orig_user_id and orig_user_id.isdigit():
                await context.bot.send_message(
                    chat_id=int(orig_user_id),
                    text=f"✉️ Admin reply: {message_text}"
                )
                await update.message.reply_text("✅ Reply sent to user.")
                return
        
        # If user is not admin, forward message to all admins
        if not BotConfig.is_admin(user.id):
            for admin_id in BotConfig.ADMIN_USER_IDS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📩 Message from user {user.first_name} (@{user.username or 'NoUsername'} | ID: {user.id}):\n{message_text}",
                    caption=str(user.id)
                )
            await update.message.reply_text("✅ Your message has been sent to the admin. They will reply here.")
            return
        
        # Default echo for admin or fallback
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
        
        from telegram import ReplyKeyboardMarkup
        keyboard = [
            ["/wallet", "/wallet_history"],
            ["Top Up", "Withdraw"],
            ["/info", "/help"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
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