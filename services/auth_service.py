import os
import hashlib
import binascii

class AuthService:
    def __init__(self):
        # Mock user database. Passwords are stored as salted PBKDF2 hashes.
        # For compatibility we set the legacy 'password' field to None so callers
        # that expect the key won't receive plaintext credentials.
        self.users = [
            {
                'id': 1,
                'username': 'admin',
                'password_hash': self._hash_password('admin123'),
                'password': None,
                'is_admin': True
            },
            {
                'id': 2,
                'username': 'user',
                'password_hash': self._hash_password('user123'),
                'password': None,
                'is_admin': False
            }
        ]

    def _hash_password(self, password, iterations=100000):
        """Hash a password using PBKDF2-HMAC-SHA256 with a per-password salt.

        Returns a string in the format: algorithm$iterations$salt_hex$hash_hex
        """
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return f"pbkdf2_sha256${iterations}${binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

    def _verify_password(self, stored_hash, password):
        """Verify a password against a stored PBKDF2 hash."""
        try:
            algo, iter_s, salt_hex, hash_hex = stored_hash.split('$')
            iterations = int(iter_s)
            salt = binascii.unhexlify(salt_hex)
            dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
            return binascii.hexlify(dk).decode() == hash_hex
        except Exception:
            return False

    def authenticate_user(self, username, password):
        """Authenticate a user by username and password"""
        for user in self.users:
            if user.get('username') != username:
                continue

            # Prefer secure hash comparison when available
            if 'password_hash' in user and user['password_hash']:
                if self._verify_password(user['password_hash'], password):
                    return user
            # Fallback for legacy entries that still have plaintext (should be migrated)
            elif 'password' in user and user['password'] is not None:
                if user['password'] == password:
                    return user
        return None

    def get_user_by_id(self, user_id):
        """Get a user by their ID"""
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None
