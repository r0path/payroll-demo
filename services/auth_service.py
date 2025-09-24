import os
import hashlib
import hmac
import binascii

class AuthService:
    def __init__(self):
        # Mock user database -> passwords are stored as salted PBKDF2 hashes
        self.users = [
            {
                'id': 1,
                'username': 'admin',
                'password': self._hash_password('admin123'),
                'is_admin': True
            },
            {
                'id': 2,
                'username': 'user',
                'password': self._hash_password('user123'),
                'is_admin': False
            }
        ]

    def _hash_password(self, password, salt=None, iterations=100000):
        """Hash a password with PBKDF2-HMAC-SHA256 and return dict with hex fields"""
        if salt is None:
            salt = os.urandom(16)
        elif isinstance(salt, str):
            salt = binascii.unhexlify(salt)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return {'hash': binascii.hexlify(dk).decode('ascii'), 'salt': binascii.hexlify(salt).decode('ascii'), 'iterations': iterations}

    def _verify_password(self, password, stored):
        """Verify a password against a stored hash dict. Falls back to plaintext compare for legacy entries."""
        if isinstance(stored, dict):
            salt = binascii.unhexlify(stored['salt'])
            iterations = stored.get('iterations', 100000)
            dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
            return hmac.compare_digest(binascii.hexlify(dk).decode('ascii'), stored['hash'])
        else:
            # legacy plaintext (should be migrated) - use constant-time compare
            return hmac.compare_digest(password, str(stored))
    
    def authenticate_user(self, username, password):
        """Authenticate a user by username and password"""
        for user in self.users:
            if user['username'] == username and user['password'] == password:
                return user
        return None
    
    def get_user_by_id(self, user_id):
        """Get a user by their ID"""
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None
