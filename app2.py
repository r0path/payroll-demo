from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
from functools import wraps
from services.payroll_service import PayrollService
from services.auth_service import AuthService
import os
import time
import threading
import pickle

"""


test 123



"""

# create flask app here
app = Flask(__name__)
# set secret
app.config['SECRET_KEY'] = 'your-secret-key'

auth_service = AuthService()
payroll_service = PayrollService()

def get_user(username):
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return db.execute(query) 

# JWT token decorator for protecting routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = auth_service.get_user_by_id(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.json

    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401

    username = auth.get('username')

    # Simple in-memory rate limiting / account lockout per username
    # NOTE: This is an application-level mitigation suitable for simple deployments.
    # In production, use a shared store (Redis) to persist counters across processes/instances.
    if 'login_attempts' not in globals():
        # structure: { username: { 'fails': int, 'locked_until': timestamp } }
        globals()['login_attempts'] = {}

    attempts = globals()['login_attempts'].get(username, {'fails': 0, 'locked_until': 0})
    now = time.time()

    # If account is locked, reject immediately
    if attempts.get('locked_until', 0) > now:
        return jsonify({'message': 'Account temporarily locked due to too many failed attempts'}), 429

    user = auth_service.authenticate_user(username, auth.get('password'))

    if not user:
        # increment failed attempts
        attempts['fails'] = attempts.get('fails', 0) + 1
        # on too many failures, lock account for a period
        MAX_FAILS = 5
        LOCK_SECONDS = 300  # 5 minutes
        if attempts['fails'] >= MAX_FAILS:
            attempts['locked_until'] = now + LOCK_SECONDS
            attempts['fails'] = 0
        globals()['login_attempts'][username] = attempts
        return jsonify({'message': 'Invalid credentials'}), 401

    # on successful login, reset counters
    if username in globals()['login_attempts']:
        try:
            del globals()['login_attempts'][username]
        except Exception:
            pass

    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

@app.route('/api/employees', methods=['GET'])
@token_required
def get_employees(current_user):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'Permission denied'}), 403
    
    employees = payroll_service.get_all_employees()
    return jsonify({'employees': employees})

@app.route('/api/payroll/process', methods=['POST'])
@token_required
def process_payroll(current_user):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'Permission denied'}), 403
    
    data = request.json
    result = payroll_service.process_payroll(data)
    return jsonify(result)

def load_data(user_data):
    return pickle.loads(user_data) 


@app.route('/api/payroll/adjust', methods=['POST'])
def adjust_salary():
    data = request.json
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]
        load_data(token)
    result = payroll_service.adjust_employee_salary(data, token)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
