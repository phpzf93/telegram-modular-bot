import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class UserDatabase:
    """Simple JSON-based user database for storing user data and wallets"""
    
    def __init__(self, db_file: str = "users.json"):
        self.db_file = db_file
        self.users = self._load_database()
    
    def _load_database(self) -> Dict:
        """Load database from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_database(self):
        """Save database to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.users, f, indent=2, default=str)
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Add or update user in database"""
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            self.users[user_id_str] = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'wallet_balance': 0.0,
                'wallet_transactions': [],
                'joined_date': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat()
            }
        else:
            # Update user info
            self.users[user_id_str]['username'] = username
            self.users[user_id_str]['first_name'] = first_name
            self.users[user_id_str]['last_active'] = datetime.now().isoformat()
        
        self._save_database()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        return self.users.get(str(user_id))
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        return list(self.users.values())
    
    def get_user_ids(self) -> List[int]:
        """Get all user IDs for broadcasting"""
        return [user['user_id'] for user in self.users.values()]
    
    def update_wallet_balance(self, user_id: int, amount: float, transaction_type: str = "manual", description: str = ""):
        """Update user wallet balance"""
        user_id_str = str(user_id)
        if user_id_str in self.users:
            old_balance = self.users[user_id_str]['wallet_balance']
            self.users[user_id_str]['wallet_balance'] += amount
            
            # Add transaction record
            transaction = {
                'amount': amount,
                'type': transaction_type,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'old_balance': old_balance,
                'new_balance': self.users[user_id_str]['wallet_balance']
            }
            self.users[user_id_str]['wallet_transactions'].append(transaction)
            
            self._save_database()
            return True
        return False
    
    def get_wallet_balance(self, user_id: int) -> float:
        """Get user wallet balance"""
        user = self.get_user(user_id)
        return user['wallet_balance'] if user else 0.0
    
    def get_wallet_transactions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user wallet transactions"""
        user = self.get_user(user_id)
        if user and 'wallet_transactions' in user:
            return user['wallet_transactions'][-limit:]
        return []
    
    def get_total_users(self) -> int:
        """Get total number of users"""
        return len(self.users)
    
    def get_total_wallet_balance(self) -> float:
        """Get total wallet balance across all users"""
        return sum(user['wallet_balance'] for user in self.users.values())