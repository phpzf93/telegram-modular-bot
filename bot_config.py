import os
from typing import List

class BotConfig:
    """Configuration class for the Telegram bot"""
    
    # Bot token - replace with your actual token
    BOT_TOKEN = "8275071760:AAFOYIYzHHPHMnONXNA0tPFA-Ys3c3VhjCs"
    
    # Admin user IDs - replace with actual admin user IDs
    ADMIN_USER_IDS: List[int] = [
        # Add your admin user IDs here
        # Example: 123456789, 987654321
    ]
    
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