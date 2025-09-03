#!/usr/bin/env python3
"""
Modular Telegram Bot
A feature-rich Telegram bot with message handling, wallet functionality, and admin functions.
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot_config import BotConfig
from handlers.message_handler import MessageHandler
from handlers.admin_handler import AdminHandler
from handlers.wallet_handler import WalletHandler
from handlers.broadcast_handler import BroadcastHandler

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    if BotConfig.ENABLE_LOGGING:
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=getattr(logging, BotConfig.LOG_LEVEL, logging.INFO)
        )
        logger = logging.getLogger(__name__)
        logger.info("Logging configured successfully")

def main():
    """Main function to run the bot"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create application
    logger.info("Initializing Telegram Bot...")
    application = Application.builder().token(BotConfig.BOT_TOKEN).build()
    
    # Add message handlers
    logger.info("Adding message handlers...")
    application.add_handler(CommandHandler("start", MessageHandler.handle_start))
    application.add_handler(CommandHandler("help", MessageHandler.handle_help))
    application.add_handler(CommandHandler("info", MessageHandler.handle_info))
    
    # Add wallet handlers
    logger.info("Adding wallet handlers...")
    application.add_handler(CommandHandler("wallet", WalletHandler.handle_wallet_balance))
    application.add_handler(CommandHandler("wallet_history", WalletHandler.handle_wallet_history))
    application.add_handler(CommandHandler("wallet_deposit", WalletHandler.handle_wallet_deposit))
    application.add_handler(CommandHandler("wallet_withdraw", WalletHandler.handle_wallet_withdraw))
    
    # Add admin handlers
    logger.info("Adding admin handlers...")
    application.add_handler(CommandHandler("admin_help", AdminHandler.handle_admin_help))
    application.add_handler(CommandHandler("admin_stats", AdminHandler.handle_admin_stats))
    application.add_handler(CommandHandler("admin_list", AdminHandler.handle_list_admins))
    application.add_handler(CommandHandler("user_list", AdminHandler.handle_user_list))
    application.add_handler(CommandHandler("add_admin", AdminHandler.handle_add_admin))
    application.add_handler(CommandHandler("remove_admin", AdminHandler.handle_remove_admin))
    application.add_handler(CommandHandler("admin_shutdown", AdminHandler.handle_shutdown))
    
    # Add admin wallet handlers
    application.add_handler(CommandHandler("admin_add_funds", WalletHandler.handle_admin_add_funds))
    application.add_handler(CommandHandler("wallet_stats", WalletHandler.handle_wallet_stats))
    
    # Add broadcast handlers
    logger.info("Adding broadcast handlers...")
    application.add_handler(CommandHandler("broadcast", BroadcastHandler.handle_broadcast))
    application.add_handler(CommandHandler("broadcast_confirm", BroadcastHandler.handle_broadcast_confirm))
    application.add_handler(CommandHandler("broadcast_cancel", BroadcastHandler.handle_broadcast_cancel))
    application.add_handler(CommandHandler("broadcast_test", BroadcastHandler.handle_broadcast_test))
    
    # Add content handlers
    logger.info("Adding content handlers...")
    from telegram.ext import MessageHandler as TgMessageHandler, filters
    from handlers.message_handler import MessageHandler as CustomMessageHandler
    application.add_handler(TgMessageHandler(filters.TEXT & ~filters.COMMAND, CustomMessageHandler.handle_text_message))
    # If you have handle_photo and handle_document methods, add them similarly:
    # application.add_handler(TgMessageHandler(filters.PHOTO, CustomMessageHandler.handle_photo))
    # application.add_handler(TgMessageHandler(filters.DOCUMENT, CustomMessageHandler.handle_document))
    
    # Start the bot
    logger.info("Starting bot...")
    logger.info(f"Bot configured with {len(BotConfig.ADMIN_USER_IDS)} admin(s)")
    
    print("🤖 Telegram Bot is starting...")
    print(f"📊 Admin users configured: {len(BotConfig.ADMIN_USER_IDS)}")
    print("🔧 To add yourself as admin, add your user ID to bot_config.py")
    print("📱 Send /start to the bot to begin!")
    print("💰 New features: Wallet system and broadcasting!")
    print("⏹️  Press Ctrl+C to stop the bot")
    
    # Set up Flask app for webhook and health check
    from flask import Flask, request, jsonify
    import os

    flask_app = Flask(__name__)

    @flask_app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'}), 200

    @flask_app.route('/telegram/webhook', methods=['POST'])
    def telegram_webhook():
        update = request.get_json(force=True)
        application.update_queue.put(update)
        return jsonify({'status': 'received'}), 200

    # Set webhook for Telegram
    webhook_url = os.environ.get('WEBHOOK_URL')
    if webhook_url:
        application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.warning("WEBHOOK_URL not set. Bot will not receive updates via webhook.")

    # Run Flask app
    flask_app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logging.error(f"Bot startup error: {e}")