"""
User Storage Module
Handles user registration and storage (in-memory with JSON file persistence)
In production, replace with a proper database (PostgreSQL, MongoDB, etc.)
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import threading

try:
    from api.config import settings
except ImportError:
    from config import settings


class UserStorage:
    """Thread-safe user storage with file persistence"""
    
    def __init__(self, storage_file: str = "users.json"):
        self.storage_file = Path(storage_file)
        self._lock = threading.Lock()
        self._users: Dict[str, Dict[str, Any]] = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from JSON file"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    self._users = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._users = {}
        else:
            self._users = {}
    
    def ensure_default_admin(self):
        """Ensure default admin exists (called lazily to avoid import-time issues)"""
        if not self._users:
            self._create_default_admin()
        else:
            # Check if admin user exists
            try:
                from api.config import settings
            except ImportError:
                from config import settings
            
            admin_username = settings.ADMIN_USERNAME
            if not self.user_exists(admin_username):
                self._create_default_admin()
    
    def _save_users(self):
        """Save users to JSON file"""
        try:
            # Create directory if it doesn't exist
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_file, 'w') as f:
                json.dump(self._users, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save users to file: {e}")
    
    def _create_default_admin(self):
        """Create default admin user from settings"""
        # Import here to avoid circular imports
        try:
            from api.auth import get_password_hash
        except ImportError:
            from auth import get_password_hash
        
        try:
            from api.config import settings
        except ImportError:
            from config import settings
        
        admin_username = settings.ADMIN_USERNAME
        admin_password = settings.ADMIN_PASSWORD
        
        # Hash the admin password, but be resilient if the preferred backend isn't available
        try:
            hashed = get_password_hash(admin_password)
        except Exception:
            # Fallback to a simple sha256 legacy format so the service remains usable
            import hashlib
            hashed = f"legacy:sha256${hashlib.sha256(admin_password.encode('utf-8')).hexdigest()}"

        self._users[admin_username] = {
            "username": admin_username,
            "hashed_password": hashed,
            "email": f"{admin_username}@example.com",
            "role": "admin",
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        self._save_users()
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        with self._lock:
            return username.lower() in {k.lower(): v for k, v in self._users.items()}
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username (case-insensitive)"""
        with self._lock:
            # Case-insensitive lookup
            for key, user in self._users.items():
                if key.lower() == username.lower():
                    return user.copy()
            return None
    
    def create_user(
        self,
        username: str,
        hashed_password: str,
        email: Optional[str] = None,
        role: str = "user"
    ) -> Dict[str, Any]:
        """Create a new user"""
        with self._lock:
            # Check if user already exists (case-insensitive)
            if self.user_exists(username):
                raise ValueError(f"Username '{username}' already exists")
            
            user_data = {
                "username": username,
                "hashed_password": hashed_password,
                "email": email or f"{username}@example.com",
                "role": role,
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }
            
            self._users[username] = user_data
            self._save_users()
            return user_data.copy()
    
    def update_user(self, username: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user data"""
        with self._lock:
            user = self.get_user(username)
            if not user:
                return None
            
            # Update allowed fields
            allowed_fields = ["email", "role", "is_active", "hashed_password"]
            for key, value in kwargs.items():
                if key in allowed_fields:
                    self._users[username][key] = value
            
            self._save_users()
            return self.get_user(username)
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        with self._lock:
            if username in self._users:
                del self._users[username]
                self._save_users()
                return True
            return False
    
    def list_users(self, active_only: bool = True) -> list:
        """List all users"""
        with self._lock:
            users = list(self._users.values())
            if active_only:
                users = [u for u in users if u.get("is_active", True)]
            # Remove sensitive data
            return [
                {
                    "username": u["username"],
                    "email": u.get("email"),
                    "role": u.get("role", "user"),
                    "created_at": u.get("created_at"),
                    "is_active": u.get("is_active", True)
                }
                for u in users
            ]
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        # Import here to avoid circular imports
        try:
            from api.auth import verify_password
        except ImportError:
            from auth import verify_password
        
        user = self.get_user(username)
        if not user:
            return False
        
        if not user.get("is_active", True):
            return False
        
        hashed_password = user.get("hashed_password")
        if not hashed_password:
            return False

        # Support legacy sha256-stored passwords (marked with prefix) for environments
        if isinstance(hashed_password, str) and hashed_password.startswith("legacy:sha256$"):
            import hashlib
            expected = hashed_password.split("$", 1)[1]
            return hashlib.sha256(password.encode('utf-8')).hexdigest() == expected

        return verify_password(password, hashed_password)


# Global user storage instance (lazy initialization)
_user_storage_instance = None

def get_user_storage():
    """Get user storage instance (singleton pattern)"""
    global _user_storage_instance
    if _user_storage_instance is None:
        _user_storage_instance = UserStorage(storage_file="users.json")
    return _user_storage_instance

# For backward compatibility, create instance but don't create admin yet
user_storage = UserStorage(storage_file="users.json")

