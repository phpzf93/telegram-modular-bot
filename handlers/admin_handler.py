from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import admin_required
from bot_config import BotConfig
from database import UserDatabase
import logging

logger = logging.getLogger(__name__)
db = UserDatabase()

class AdminHandler:
    """Handle admin-only commands and functions"""
    
    @staticmethod
    @admin_required
    async def handle_admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin help menu"""
        help_message = "🔧 **Admin Commands:**\n\n"
        help_message += "📊 **Information:**\n"
        help_message += "• `/admin_help` - Show this admin menu\n"
        help_message += "• `/admin_stats` - Show bot statistics\n"
        help_message += "• `/admin_list` - List all admins\n\n"
        help_message += "👥 **User Management:**\n"
        help_message += "• `/add_admin <user_id>` - Add new admin\n"
        help_message += "• `/remove_admin <user_id>` - Remove admin\n"
        help_message += "• `/user_list` - List all users\n\n"
        help_message += "📢 **Broadcasting:**\n"
        help_message += "• `/broadcast <message>` - Send message to all users\n"
        help_message += "• `/broadcast_confirm` - Confirm pending broadcast\n"
        help_message += "• `/broadcast_cancel` - Cancel pending broadcast\n"
        help_message += "• `/broadcast_test <message>` - Test broadcast to admins\n\n"
        help_message += "💰 **Wallet Management:**\n"
        help_message += "• `/admin_add_funds <user_id> <amount>` - Add funds to user\n"
        help_message += "• `/wallet_stats` - Show wallet statistics\n\n"
        help_message += "⚠️ **System:**\n"
        help_message += "• `/admin_shutdown` - Shutdown bot (use with caution)"
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    @staticmethod
    @admin_required
    async def handle_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        total_users = db.get_total_users()
        total_wallet_balance = db.get_total_wallet_balance()
        
        stats_message = "📊 **Bot Statistics:**\n\n"
        stats_message += f"🔧 Total Admins: {len(BotConfig.ADMIN_USER_IDS)}\n"
        stats_message += f"👥 Total Users: {total_users}\n"
        stats_message += f"💰 Total Wallet Balance: ${total_wallet_balance:.2f}\n"
        stats_message += f"🤖 Bot Token: `{BotConfig.BOT_TOKEN[:10]}...`\n"
        stats_message += f"📝 Logging: {'✅ Enabled' if BotConfig.ENABLE_LOGGING else '❌ Disabled'}\n"
        stats_message += f"📊 Log Level: {BotConfig.LOG_LEVEL}"
        
        await update.message.reply_text(stats_message, parse_mode='Markdown')
    
    @staticmethod
    @admin_required
    async def handle_list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all admin users"""
        if not BotConfig.ADMIN_USER_IDS:
            await update.message.reply_text("👥 No admins configured yet.")
            return
        
        admin_list = "👥 **Current Admins:**\n\n"
        for i, admin_id in enumerate(BotConfig.ADMIN_USER_IDS, 1):
            admin_data = db.get_user(admin_id)
            if admin_data:
                admin_list += f"{i}. {admin_data['first_name']} (@{admin_data['username'] or 'N/A'}) - `{admin_id}`\n"
            else:
                admin_list += f"{i}. User ID: `{admin_id}` (Not in database)\n"
        
        await update.message.reply_text(admin_list, parse_mode='Markdown')
    
    @staticmethod
    @admin_required
    async def handle_user_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all users in database"""
        users = db.get_all_users()
        
        if not users:
            await update.message.reply_text("👥 No users found in database.")
            return
        
        # Show first 20 users to avoid message length limits
        user_list = f"👥 **User List** (Showing {min(20, len(users))} of {len(users)} users):\n\n"
        
        for i, user in enumerate(users[:20], 1):
            user_list += f"{i}. {user['first_name']} (@{user['username'] or 'N/A'})\n"
            user_list += f"   💰 ${user['wallet_balance']:.2f} | ID: `{user['user_id']}`\n\n"
        
        if len(users) > 20:
            user_list += f"... and {len(users) - 20} more users"
        
        await update.message.reply_text(user_list, parse_mode='Markdown')
    
    @staticmethod
    @admin_required
    async def handle_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a new admin user"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /add_admin <user_id>")
            return
        
        try:
            user_id = int(context.args[0])
            if BotConfig.add_admin(user_id):
                await update.message.reply_text(f"✅ User {user_id} added as admin successfully!")
                logger.info(f"New admin added: {user_id}")
            else:
                await update.message.reply_text(f"⚠️ User {user_id} is already an admin.")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
    
    @staticmethod
    @admin_required
    async def handle_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove an admin user"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /remove_admin <user_id>")
            return
        
        try:
            user_id = int(context.args[0])
            if user_id == update.effective_user.id:
                await update.message.reply_text("❌ You cannot remove yourself as admin.")
                return
            
            if BotConfig.remove_admin(user_id):
                await update.message.reply_text(f"✅ User {user_id} removed from admin list successfully!")
                logger.info(f"Admin removed: {user_id}")
            else:
                await update.message.reply_text(f"⚠️ User {user_id} is not an admin.")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
    
    @staticmethod
    @admin_required
    async def handle_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Shutdown the bot (placeholder)"""
        await update.message.reply_text("⚠️ Shutdown command received. In a production environment, this would stop the bot.")
        logger.warning(f"Shutdown command issued by admin {update.effective_user.id}")