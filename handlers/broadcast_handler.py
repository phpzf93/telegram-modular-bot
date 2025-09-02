from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import admin_required
from database import UserDatabase
import asyncio
import logging

logger = logging.getLogger(__name__)
db = UserDatabase()

class BroadcastHandler:
    """Handle broadcast functionality"""
    
    @staticmethod
    @admin_required
    async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast a message to all users"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /broadcast <message>\nExample: /broadcast Hello everyone! This is an important announcement.")
            return
        
        message = " ".join(context.args)
        user_ids = db.get_user_ids()
        
        if not user_ids:
            await update.message.reply_text("❌ No users found in database to broadcast to.")
            return
        
        # Show confirmation
        confirm_msg = f"📢 **Broadcast Preview:**\n\n{message}\n\n"
        confirm_msg += f"👥 This message will be sent to {len(user_ids)} users.\n"
        confirm_msg += "Use /broadcast_confirm to send or /broadcast_cancel to cancel."
        
        # Store broadcast data in context for confirmation
        context.user_data['pending_broadcast'] = {
            'message': message,
            'user_ids': user_ids,
            'admin_id': update.effective_user.id
        }
        
        await update.message.reply_text(confirm_msg, parse_mode='Markdown')
    
    @staticmethod
    @admin_required
    async def handle_broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm and send the broadcast"""
        if 'pending_broadcast' not in context.user_data:
            await update.message.reply_text("❌ No pending broadcast found. Use /broadcast <message> first.")
            return
        
        broadcast_data = context.user_data['pending_broadcast']
        message = broadcast_data['message']
        user_ids = broadcast_data['user_ids']
        
        # Start broadcasting
        status_msg = await update.message.reply_text("📡 Starting broadcast...")
        
        success_count = 0
        failed_count = 0
        
        # Add broadcast header
        broadcast_message = f"📢 **Broadcast Message**\n\n{message}\n\n_This is an official broadcast from the bot administrators._"
        
        for user_id in user_ids:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=broadcast_message,
                    parse_mode='Markdown'
                )
                success_count += 1
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to send broadcast to user {user_id}: {e}")
        
        # Update status
        final_message = f"✅ **Broadcast Completed!**\n\n"
        final_message += f"📤 Successfully sent: {success_count}\n"
        final_message += f"❌ Failed to send: {failed_count}\n"
        final_message += f"📊 Total users: {len(user_ids)}"
        
        await status_msg.edit_text(final_message, parse_mode='Markdown')
        
        # Clear pending broadcast
        del context.user_data['pending_broadcast']
        
        logger.info(f"Broadcast completed by admin {update.effective_user.id}: {success_count} success, {failed_count} failed")
    
    @staticmethod
    @admin_required
    async def handle_broadcast_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel pending broadcast"""
        if 'pending_broadcast' not in context.user_data:
            await update.message.reply_text("❌ No pending broadcast found.")
            return
        
        del context.user_data['pending_broadcast']
        await update.message.reply_text("✅ Broadcast cancelled.")
    
    @staticmethod
    @admin_required
    async def handle_broadcast_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a test broadcast to admins only"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /broadcast_test <message>")
            return
        
        from bot_config import BotConfig
        message = " ".join(context.args)
        admin_ids = BotConfig.ADMIN_USER_IDS
        
        if not admin_ids:
            await update.message.reply_text("❌ No admin users configured.")
            return
        
        success_count = 0
        failed_count = 0
        
        test_message = f"🧪 **Test Broadcast**\n\n{message}\n\n_This is a test broadcast sent only to administrators._"
        
        for admin_id in admin_ids:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=test_message,
                    parse_mode='Markdown'
                )
                success_count += 1
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to send test broadcast to admin {admin_id}: {e}")
        
        result_message = f"🧪 **Test Broadcast Results:**\n\n"
        result_message += f"📤 Sent to {success_count} admins\n"
        result_message += f"❌ Failed: {failed_count}"
        
        await update.message.reply_text(result_message, parse_mode='Markdown')