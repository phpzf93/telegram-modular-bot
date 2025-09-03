import os
from typing import List

class BotConfig:
    """Configuration class for the Telegram bot"""
    
    # Bot token - loaded from environment variable
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    # Xendit API key - loaded from environment variable
    XENDIT_API_KEY = os.environ.get("XENDIT_API_KEY")
    
    # Admin user IDs - replace with actual admin user IDs
    ADMIN_USER_IDS: List[int] = [8209675920]
    # Add your admin user IDs here
    # Example: 123456789, 987654321
    
    # Bot settings
    ENABLE_LOGGING = True
    LOG_LEVEL = "INFO"
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is an admin"""
        return user_id in cls.ADMIN_USER_IDS
    
    @classmethod
    def add_admin(cls, user_id: int) -> bool:
        """Add a new admin user"""
        if user_id not in cls.ADMIN_USER_IDS:
            cls.ADMIN_USER_IDS.append(user_id)
            return True
        return False
    
    @classmethod
    def remove_admin(cls, user_id: int) -> bool:
        """Remove an admin user"""
        if user_id in cls.ADMIN_USER_IDS:
            cls.ADMIN_USER_IDS.remove(user_id)
            return True
        return False