import os
import hashlib
import binascii

class AuthService:
    def __init__(self):
        # Mock user database with plaintext passwords (for demo); these will be hashed at init
        raw_users = [
            {
                'id': 1,
                'username': 'admin',
                'password': 'admin123',  # plain text in source for demo only
                'is_admin': True
            },
            {
                'id': 2,
                'username': 'user',
                'password': 'user123',  # plain text in source for demo only
                'is_admin': False
            }
        ]

        # Convert plaintext passwords to salted PBKDF2-HMAC-SHA256 hashes
        self.users = []
        for u in raw_users:
            salt = os.urandom(16)
            pwd_hash = hashlib.pbkdf2_hmac('sha256', u['password'].encode('utf-8'), salt, 100000)
            pwd_hash_hex = binascii.hexlify(pwd_hash).decode('ascii')
            salt_hex = binascii.hexlify(salt).decode('ascii')
            self.users.append({
                'id': u['id'],
                'username': u['username'],
                'password_hash': pwd_hash_hex,
                'salt': salt_hex,
                'is_admin': u['is_admin']
            })
    
    def authenticate_user(self, username, password):
        """Authenticate a user by username and password using PBKDF2-HMAC-SHA256"""
        for user in self.users:
            if user['username'] == username:
                salt = binascii.unhexlify(user['salt'].encode('ascii'))
                pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
                pwd_hash_hex = binascii.hexlify(pwd_hash).decode('ascii')
                if pwd_hash_hex == user['password_hash']:
                    return user
                return None
        return None
    
    def get_user_by_id(self, user_id):
        """Get a user by their ID"""
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None
