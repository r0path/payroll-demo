import os
import hashlib
import binascii
import hmac

class AuthService:
    def __init__(self):
        # Mock user database (store plaintext passwords initially for setup)
        self.users = [
            {
                'id': 1,
                'username': 'admin',
                'password': 'admin123',  # Will be replaced with a hashed password at initialization
                'is_admin': True
            },
            {
                'id': 2,
                'username': 'user',
                'password': 'user123',
                'is_admin': False
            }
        ]
        # Migrate plaintext passwords to salted PBKDF2 hashes
        for user in self.users:
            if 'password' in user:
                salt = os.urandom(16)
                pw_hash = self._hash_password(user.pop('password'), salt)
                user['salt'] = binascii.hexlify(salt).decode('ascii')
                user['password_hash'] = pw_hash

    def _hash_password(self, password, salt, iterations=100_000):
        """Hash a password using PBKDF2-HMAC-SHA256."""
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return binascii.hexlify(dk).decode('ascii')

    def _verify_password(self, password, salt_hex, stored_hash, iterations=100_000):
        """Verify a password against the stored hash using constant-time comparison."""
        salt = binascii.unhexlify(salt_hex)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        candidate = binascii.hexlify(dk).decode('ascii')
        return hmac.compare_digest(candidate, stored_hash)

    def authenticate_user(self, username, password):
        """Authenticate a user by username and password"""
        for user in self.users:
            if user.get('username') == username:
                # If user has migrated to hashing, verify against hash
                if 'password_hash' in user and 'salt' in user:
                    if self._verify_password(password, user['salt'], user['password_hash']):
                        return user
                # Fallback for legacy plaintext (should be migrated at init)
                elif user.get('password') == password:
                    return user
        return None

    def get_user_by_id(self, user_id):
        """Get a user by their ID"""
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None
