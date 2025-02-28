class AuthService:
    def __init__(self):
        # Mock user database
        self.users = [
            {
                'id': 1,
                'username': 'admin',
                'password': 'admin123',  # In a real app, this would be hashed
                'is_admin': True
            },
            {
                'id': 2,
                'username': 'user',
                'password': 'user123',
                'is_admin': False
            }
        ]
    
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
