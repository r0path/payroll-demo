import os
import hashlib
import binascii
import hmac

def _hash_password(password, iterations=100000):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

def _verify_password(stored, provided):
    try:
        algo, iterations, salt_hex, hash_hex = stored.split('$')
        iterations = int(iterations)
        salt = binascii.unhexlify(salt_hex)
        stored_dk = binascii.unhexlify(hash_hex)
        new_dk = hashlib.pbkdf2_hmac('sha256', provided.encode(), salt, iterations)
        return hmac.compare_digest(new_dk, stored_dk)
    except Exception:
        return False

class AuthService:
    def __init__(self):
        # Mock user database
        self.users = [
            {
                'id': 1,
                'username': 'admin',
                'password': _hash_password('admin123'),
                'is_admin': True
            },
            {
                'id': 2,
                'username': 'user',
                'password': _hash_password('user123'),
                'is_admin': False
            }
        ]
    
    def authenticate_user(self, username, password):
        """Authenticate a user by username and password"""
        for user in self.users:
            if user['username'] == username and _verify_password(user['password'], password):
                return user
        return None
    
    def get_user_by_id(self, user_id):
        """Get a user by their ID"""
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None
