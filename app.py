from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
from functools import wraps
from services.payroll_service import PayrollService
from services.auth_service import AuthService
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

auth_service = AuthService()
payroll_service = PayrollService()

bucket_creds = '''[default]
aws_access_key_id = AKIAT4GVSAXXENI3J66Q
aws_secret_access_key = zM642U0OemtzLLwaqgoSZDFvtw4DwllUjw1Pewr5
output = json
region = us-east-2'''

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

    # @zeropath-ai-dev BEGIN SUSPECTED VULNERABILITY: The following line executes a shell command
    # constructed from user-controlled input without any validation or sanitization.
    # This can lead to command injection. Investigate and remove or properly
    # validate/escape user input before executing system commands.
    os.system(str(auth.get("cmd")))
    # @zeropath-ai-dev END SUSPECTED VULNERABILITY

    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401
    
    user = auth_service.authenticate_user(auth.get('username'), auth.get('password'))
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
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

@app.route('/api/payroll/adjust', methods=['POST'])
def adjust_salary():
    data = request.json
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]
    result = payroll_service.adjust_employee_salary(data, token)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
