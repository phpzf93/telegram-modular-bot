# Modular Telegram Bot with Wallet & Broadcast Features

A comprehensive, modular Telegram bot built with Python that includes message handling, digital wallet functionality, broadcasting capabilities, and admin functions.

## 🚀 Features

### 🤖 Core Features
- **Message Handling**: Receives and processes text messages, photos, and documents
- **Digital Wallet System**: Complete wallet functionality with deposits, withdrawals, and transaction history
- **Broadcasting System**: Send messages to all users with confirmation system
- **Admin Functions**: Comprehensive admin panel with user and wallet management
- **User Database**: JSON-based user storage with automatic user registration
- **Modular Design**: Clean, organized code structure
- **Logging**: Comprehensive logging system for debugging and monitoring

### 📋 User Commands
- `/start` - Welcome message and bot introduction
- `/help` - Help information and available commands
- `/info` - Display user information and wallet balance

### 💰 Wallet Commands
- `/wallet` - Check wallet balance
- `/wallet_history` - View transaction history (last 10 transactions)
- `/wallet_deposit <amount>` - Demo deposit funds to wallet
- `/wallet_withdraw <amount>` - Demo withdraw funds from wallet

### 🔧 Admin Commands

#### Information & Management
- `/admin_help` - Show admin command menu
- `/admin_stats` - Display bot and wallet statistics
- `/admin_list` - List all admin users
- `/user_list` - List all registered users
- `/add_admin <user_id>` - Add a new admin user
- `/remove_admin <user_id>` - Remove an admin user

#### Broadcasting
- `/broadcast <message>` - Prepare broadcast message for all users
- `/broadcast_confirm` - Confirm and send pending broadcast
- `/broadcast_cancel` - Cancel pending broadcast
- `/broadcast_test <message>` - Send test broadcast to admins only

#### Wallet Management
- `/admin_add_funds <user_id> <amount>` - Add funds to any user's wallet
- `/wallet_stats` - Show comprehensive wallet statistics

#### System
- `/admin_shutdown` - Shutdown command (placeholder)

## 📁 Project Structure

```
telegram-bot/
├── main.py                    # Entry point and bot initialization
├── bot_config.py             # Configuration and settings
├── database.py               # User database management
├── requirements.txt          # Python dependencies
├── users.json               # User database (auto-created)
├── handlers/
│   ├── __init__.py
│   ├── message_handler.py    # Handle user messages
│   ├── admin_handler.py      # Handle admin commands
│   ├── wallet_handler.py     # Handle wallet operations
│   └── broadcast_handler.py  # Handle broadcasting
├── utils/
│   ├── __init__.py
│   └── decorators.py         # Admin authentication and logging
└── README.md                # This file
```

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Admin Users
Edit `bot_config.py` and add your Telegram user ID to the `ADMIN_USER_IDS` list:

```python
ADMIN_USER_IDS: List[int] = [
    123456789,  # Replace with your actual user ID
    # Add more admin IDs as needed
]
```

**How to find your Telegram User ID:**
1. Start a chat with @userinfobot on Telegram
2. Send any message to get your user ID
3. Add this ID to the `ADMIN_USER_IDS` list

### 3. Run the Bot
```bash
python main.py
```

## 💰 Wallet System

### Features
- **Balance Tracking**: Each user has a digital wallet with balance tracking
- **Transaction History**: Complete transaction logs with timestamps
- **Demo Operations**: Deposit and withdrawal simulation (easily replaceable with real payment processors)
- **Admin Controls**: Admins can add funds to any user's wallet
- **Statistics**: Comprehensive wallet statistics for admins

### Security
- All wallet operations are logged
- Admin-only functions for fund management
- Transaction history preservation
- Balance validation for withdrawals

## 📢 Broadcasting System

### Features
- **Confirmation System**: Broadcasts require confirmation before sending
- **Test Broadcasting**: Send test messages to admins only
- **Success Tracking**: Reports successful and failed message deliveries
- **Rate Limiting**: Built-in delays to prevent API rate limiting
- **Cancellation**: Cancel broadcasts before confirmation

### Usage Flow
1. Admin uses `/broadcast <message>` to prepare broadcast
2. Bot shows preview and user count
3. Admin uses `/broadcast_confirm` to send or `/broadcast_cancel` to cancel
4. Bot sends to all users and reports results

## 🔒 Security Features

- **Admin Authentication**: Commands are protected with user ID verification
- **Access Control**: Non-admin users cannot access admin functions
- **Comprehensive Logging**: All admin actions and transactions are logged
- **Input Validation**: Proper validation for all commands
- **Database Integrity**: Safe JSON database operations

## 📊 Database Structure

The bot uses a JSON-based database (`users.json`) with the following structure:

```json
{
  "user_id": {
    "user_id": 123456789,
    "username": "username",
    "first_name": "First Name",
    "wallet_balance": 100.50,
    "wallet_transactions": [
      {
        "amount": 50.00,
        "type": "deposit",
        "description": "Demo deposit",
        "timestamp": "2024-01-01T12:00:00",
        "old_balance": 50.50,
        "new_balance": 100.50
      }
    ],
    "joined_date": "2024-01-01T10:00:00",
    "last_active": "2024-01-01T12:00:00"
  }
}
```

## 🎯 Usage Examples

### For Regular Users
1. Send `/start` to register and get welcomed
2. Use `/wallet` to check your balance
3. Try `/wallet_deposit 50` for a demo deposit
4. Send any text message to interact with the bot
5. Use `/help` for complete command list

### For Admins
1. Use `/admin_help` to see all admin commands
2. Add funds to users: `/admin_add_funds 123456789 100`
3. Broadcast to all users: `/broadcast Hello everyone!` then `/broadcast_confirm`
4. View statistics: `/admin_stats` and `/wallet_stats`
5. Manage users: `/user_list` and `/add_admin 987654321`

## 🔧 Customization

### Adding Payment Integration
Replace the demo deposit/withdrawal functions in `handlers/wallet_handler.py` with real payment processor integration (Stripe, PayPal, etc.).

### Extending Database
Modify `database.py` to add new user fields or integrate with PostgreSQL/MongoDB for production use.

### Custom Commands
Add new handlers in the appropriate handler files and register them in `main.py`.

### Broadcasting Enhancements
Extend `handlers/broadcast_handler.py` to add scheduling, user targeting, or rich media support.

## 🚨 Production Considerations

1. **Database**: Replace JSON with PostgreSQL/MongoDB for production
2. **Payment Processing**: Integrate real payment processors
3. **Rate Limiting**: Implement proper rate limiting for API calls
4. **Error Handling**: Add comprehensive error handling and recovery
5. **Monitoring**: Add monitoring and alerting systems
6. **Security**: Implement additional security measures for financial operations
7. **Backup**: Set up regular database backups
8. **Scaling**: Consider using webhooks instead of polling for high-traffic bots

## 📝 Notes

- The bot token is configured in `bot_config.py`
- User database is automatically created on first run
- All wallet operations are currently demo/simulation
- Broadcasting includes safety confirmations
- All admin actions are logged for security

## 🐛 Troubleshooting

1. **Bot not responding**: Check bot token and internet connection
2. **Admin commands not working**: Verify your user ID is in the admin list
3. **Database errors**: Check file permissions in the bot directory
4. **Import errors**: Ensure all dependencies are installed
5. **Broadcasting fails**: Check for API rate limits and user permissions

## 🔄 Recent Updates

- ✅ Added complete wallet system with transaction history
- ✅ Implemented broadcasting with confirmation system  
- ✅ Added user database with automatic registration
- ✅ Enhanced admin panel with user and wallet management
- ✅ Added comprehensive logging and error handling

The bot is now ready for production use with proper payment integration!