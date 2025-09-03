from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import log_message, admin_required
from database import UserDatabase
import logging
from utils.xendit_api import create_invoice, create_withdrawal

logger = logging.getLogger(__name__)
db = UserDatabase()

class WalletHandler:
    """Handle wallet-related commands and functions"""

    @staticmethod
    @log_message
    async def handle_wallet_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's wallet balance"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        balance = db.get_wallet_balance(user.id)
        message = f"\U0001F4B0 **Your Wallet**\n\n"
        message += f"\U0001F464 User: {user.first_name}\n"
        message += f"\U0001F4B5 Balance: **${balance:.2f}**\n\n"
        message += "\U0001F4CB **Wallet Commands:**\n"
        message += "• `/wallet` - Check balance\n"
        message += "• `/wallet_history` - Transaction history\n"
        message += "• `/wallet_deposit <amount>` - Request deposit\n"
        message += "• `/wallet_withdraw <amount>` - Request withdrawal"
        await update.message.reply_text(message, parse_mode='Markdown')

    @staticmethod
    @log_message
    async def handle_wallet_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's wallet transaction history"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        transactions = db.get_wallet_transactions(user.id, limit=10)
        if not transactions:
            await update.message.reply_text("\U0001F4DD No wallet transactions found.")
            return
        message = f"\U0001F4CA **Wallet History** (Last 10 transactions)\n\n"
        for i, tx in enumerate(reversed(transactions), 1):
            amount_str = f"+${tx['amount']:.2f}" if tx['amount'] > 0 else f"-${abs(tx['amount']):.2f}"
            message += f"{i}. {amount_str} - {tx['type']}\n"
            message += f"   \U0001F4B0 Balance: ${tx['new_balance']:.2f}\n"
            if tx['description']:
                message += f"   \U0001F4DD {tx['description']}\n"
            message += f"   \U0001F4C5 {tx['timestamp'][:19].replace('T', ' ')}\n\n"
        await update.message.reply_text(message, parse_mode='Markdown')

    @staticmethod
    @log_message
    async def handle_wallet_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Initiate deposit using Xendit invoice"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        args = context.args
        if not args or not args[0].replace('.', '', 1).isdigit():
            await update.message.reply_text("Usage: /wallet_deposit <amount>")
            return
        amount = float(args[0])
        await update.message.reply_text("Creating payment invoice...")
        invoice = await create_invoice(amount, user.id)
        if invoice.get("error"):
            await update.message.reply_text(f"Error creating invoice: {invoice['error']}")
            return
        pay_url = invoice.get("invoice_url")
        if pay_url:
            await update.message.reply_text(f"Please pay using this link: {pay_url}")
        else:
            await update.message.reply_text("Failed to get payment link.")

    @staticmethod
    @log_message
    async def handle_wallet_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Initiate withdrawal using Xendit disbursement"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        args = context.args
        if len(args) < 4:
            await update.message.reply_text(
                "Usage: /wallet_withdraw <amount> <bank_code> <account_number> <account_holder_name>\n"
                "Example: /wallet_withdraw 100 BCA 1234567890 John Doe"
            )
            return
        amount = float(args[0])
        bank_code = args[1]
        account_number = args[2]
        account_holder_name = " ".join(args[3:])
        await update.message.reply_text("Processing withdrawal...")
        result = await create_withdrawal(amount, user.id, bank_code, account_number, account_holder_name)
        if result.get("error"):
            await update.message.reply_text(f"Error: {result['error']}")
        else:
            await update.message.reply_text(f"Withdrawal request submitted! Status: {result.get('status', 'unknown')}")
        """Handle wallet deposit request (demo)"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /wallet_deposit <amount>\nExample: /wallet_deposit 50.00")
            return
        
        try:
            amount = float(context.args[0])
            if amount <= 0:
                await update.message.reply_text("❌ Amount must be greater than 0.")
                return
            
            # In a real implementation, you would integrate with payment processors
            # For demo purposes, we'll simulate a successful deposit
            db.update_wallet_balance(user.id, amount, "deposit", f"Demo deposit of ${amount:.2f}")
            new_balance = db.get_wallet_balance(user.id)
            
            message = f"✅ **Deposit Successful!**\n\n"
            message += f"💵 Amount: +${amount:.2f}\n"
            message += f"💰 New Balance: ${new_balance:.2f}\n\n"
            message += "⚠️ *This is a demo transaction. In production, this would integrate with real payment systems.*"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.info(f"Demo deposit: User {user.id} deposited ${amount:.2f}")
            
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a valid number.")
    
    @staticmethod
    @log_message
    async def handle_wallet_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle wallet withdrawal request (demo)"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /wallet_withdraw <amount>\nExample: /wallet_withdraw 25.00")
            return
        
        try:
            amount = float(context.args[0])
            if amount <= 0:
                await update.message.reply_text("❌ Amount must be greater than 0.")
                return
            
            current_balance = db.get_wallet_balance(user.id)
            if amount > current_balance:
                await update.message.reply_text(f"❌ Insufficient funds. Your balance is ${current_balance:.2f}")
                return
            
            # In a real implementation, you would process the withdrawal
            # For demo purposes, we'll simulate a successful withdrawal
            db.update_wallet_balance(user.id, -amount, "withdrawal", f"Demo withdrawal of ${amount:.2f}")
            new_balance = db.get_wallet_balance(user.id)
            
            message = f"✅ **Withdrawal Successful!**\n\n"
            message += f"💵 Amount: -${amount:.2f}\n"
            message += f"💰 New Balance: ${new_balance:.2f}\n\n"
            message += "⚠️ *This is a demo transaction. In production, this would process real withdrawals.*"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.info(f"Demo withdrawal: User {user.id} withdrew ${amount:.2f}")
            
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a valid number.")
    
    @staticmethod
    @admin_required
    async def handle_admin_add_funds(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin command to add funds to user wallet"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /admin_add_funds <user_id> <amount>\nExample: /admin_add_funds 123456789 100.00")
            return
        
        try:
            target_user_id = int(context.args[0])
            amount = float(context.args[1])
            
            if amount <= 0:
                await update.message.reply_text("❌ Amount must be greater than 0.")
                return
            
            user = db.get_user(target_user_id)
            if not user:
                await update.message.reply_text(f"❌ User {target_user_id} not found in database.")
                return
            
            db.update_wallet_balance(target_user_id, amount, "admin_credit", f"Admin credit by {update.effective_user.first_name}")
            new_balance = db.get_wallet_balance(target_user_id)
            
            message = f"✅ **Funds Added Successfully!**\n\n"
            message += f"👤 User: {user['first_name']} ({target_user_id})\n"
            message += f"💵 Amount Added: +${amount:.2f}\n"
            message += f"💰 New Balance: ${new_balance:.2f}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.info(f"Admin {update.effective_user.id} added ${amount:.2f} to user {target_user_id}")
            
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID or amount. Please check your input.")
    
    @staticmethod
    @admin_required
    async def handle_wallet_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin command to show wallet statistics"""
        total_users = db.get_total_users()
        total_balance = db.get_total_wallet_balance()
        
        users_with_balance = len([u for u in db.get_all_users() if u['wallet_balance'] > 0])
        
        message = f"📊 **Wallet Statistics**\n\n"
        message += f"👥 Total Users: {total_users}\n"
        message += f"💰 Total Balance: ${total_balance:.2f}\n"
        message += f"💵 Users with Balance: {users_with_balance}\n"
        message += f"📈 Average Balance: ${total_balance/total_users if total_users > 0 else 0:.2f}"
        
        await update.message.reply_text(message, parse_mode='Markdown')