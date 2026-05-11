from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
from functools import wraps
from services.payroll_service import PayrollService
from services.auth_service import AuthService
from services.export_service import ExportService
import os

app = Flask(__name__)

# Configuration section
# Load secrets from environment for security best practices
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())

auth_service = AuthService()
payroll_service = PayrollService()
export_service = ExportService()

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
@token_required
def adjust_salary(current_user):
    data = request.json
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]
    result = payroll_service.adjust_employee_salary(data, token)
    return jsonify(result)

@app.route('/api/export/paystub', methods=['POST'])
@token_required
def export_paystub(current_user):
    """Render a single paystub PDF and return the path."""
    data = request.json or {}
    employee_id = data.get('employee_id', '')
    template = data.get('template', 'standard')
    path = export_service.render_paystub_pdf(employee_id, template)
    return jsonify({'path': path})


@app.route('/api/export/archive-period', methods=['POST'])
@token_required
def archive_period(current_user):
    """Bundle every paystub for a pay period into a single zip."""
    data = request.json or {}
    period = data.get('period', '')
    name = data.get('name', 'period-archive')
    path = export_service.archive_period(period, name)
    return jsonify({'archive': path})


@app.route('/api/export/push', methods=['POST'])
@token_required
def push_to_finance(current_user):
    """Push an existing archive to finance's intake host."""
    data = request.json or {}
    archive = data.get('archive', '')
    host = data.get('host', '')
    code = export_service.push_to_finance(archive, host)
    return jsonify({'exit_code': code})


if __name__ == '__main__':
    app.run(debug=True)
