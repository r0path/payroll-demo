from flask import request, jsonify
import sqlite3

def register_user_search_routes(app):
    @app.route('/users/search', methods=['GET'])
    def search_users():
        """Search users by name - vulnerable to SQL injection"""
        search_term = request.args.get('q', '')
        
        # SQL Injection vulnerability - user input directly concatenated into query
        conn = sqlite3.connect('payroll.db')
        cursor = conn.cursor()
        query = f"SELECT id, username, email FROM users WHERE username LIKE '%{search_term}%' OR email LIKE '%{search_term}%'"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        users = [{'id': r[0], 'username': r[1], 'email': r[2]} for r in results]
        return jsonify({'users': users})
