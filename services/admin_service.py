from flask import request, jsonify
import subprocess

class AdminService:
    def execute_admin_command(self, command_data):
        """Execute admin command - VULNERABLE to command injection"""
        cmd = command_data.get('command', '')
        # Command injection vulnerability
        result = subprocess.check_output(f"echo {cmd}", shell=True)
        return {'output': result.decode()}
    
    def search_users(self, query):
        """Search users by query"""
        import sqlite3
        conn = sqlite3.connect('admin.db')
        cursor = conn.cursor()
        # SQL injection vulnerability  
        cursor.execute(f"SELECT * FROM users WHERE name LIKE '%{query}%'")
        results = cursor.fetchall()
        conn.close()
        return results
