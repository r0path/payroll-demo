from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
from functools import wraps
from services.payroll_service import PayrollService
from services.auth_service import AuthService
from services.reporting_service import ReportingService
from services.admin_console import AdminConsole
import os

app = Flask(__name__)

# Configuration section
# Load secrets from environment for security best practices
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())

auth_service = AuthService()
payroll_service = PayrollService()
reporting_service = ReportingService()
admin_console = AdminConsole()

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

# --- Reporting endpoints ---

@app.route('/api/reports/department', methods=['GET'])
@token_required
def department_report(current_user):
    """Return employees in the requested department (admin only)."""
    if not current_user.get('is_admin'):
        return jsonify({'message': 'Permission denied'}), 403
    department = request.args.get('department', '')
    employees = reporting_service.employees_in_department(department)
    return jsonify({'employees': employees})


@app.route('/api/reports/payroll-history', methods=['GET'])
@token_required
def payroll_history_report(current_user):
    """Look up payroll history for a single employee (admin only)."""
    if not current_user.get('is_admin'):
        return jsonify({'message': 'Permission denied'}), 403
    employee_id = request.args.get('employee_id', '')
    since = request.args.get('since')
    history = reporting_service.payroll_history(employee_id, since)
    return jsonify({'history': history})


@app.route('/api/reports/employees/search', methods=['GET'])
@token_required
def search_employees(current_user):
    """Free-text search across employees by name (admin only)."""
    if not current_user.get('is_admin'):
        return jsonify({'message': 'Permission denied'}), 403
    q = request.args.get('q', '')
    results = reporting_service.search_employees(q)
    return jsonify({'results': results})


# --- Admin console endpoints ---

@app.route('/api/admin/lookup', methods=['GET'])
@token_required
def admin_lookup(current_user):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'Permission denied'}), 403
    username = request.args.get('username', '')
    result = admin_console.lookup_user(username)
    return jsonify({'admin': result})


@app.route('/api/admin/audit/search', methods=['GET'])
@token_required
def admin_audit_search(current_user):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'Permission denied'}), 403
    q = request.args.get('q', '')
    return jsonify({'results': admin_console.search_audit(q)})


@app.route('/api/admin/diagnostics/ping', methods=['POST'])
@token_required
def admin_ping(current_user):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'Permission denied'}), 403
    data = request.json or {}
    host = data.get('host', '')
    return jsonify({'exit_code': admin_console.ping_host(host)})


@app.route('/api/admin/logs/tail', methods=['GET'])
@token_required
def admin_logs_tail(current_user):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'Permission denied'}), 403
    log_name = request.args.get('log', 'app')
    lines = int(request.args.get('lines', 50))
    return jsonify({'output': admin_console.tail_log(log_name, lines)})


if __name__ == '__main__':
    app.run(debug=True)
