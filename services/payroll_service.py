from models.employee import Employee
from models.payroll import Payroll
from utils.salary_calculator import SalaryCalculator
from utils.payroll_processor import PayrollProcessor

class PayrollService:
    def __init__(self):
        self.employees = [
            {"id": 1, "name": "John Doe", "position": "Developer", "base_salary": 5000},
            {"id": 2, "name": "Jane Smith", "position": "Manager", "base_salary": 7000},
            {"id": 3, "name": "Bob Johnson", "position": "Designer", "base_salary": 4500}
        ]
        self.salary_calculator = SalaryCalculator()
        self.payroll_processor = PayrollProcessor()
    
    def get_all_employees(self):
        """Return all employees"""
        return self.employees
    
    def get_employee_by_id(self, employee_id):
        """Get an employee by their ID"""
        for employee in self.employees:
            if employee["id"] == employee_id:
                return employee
        return None
    
    def process_payroll(self, data):
        """Process payroll for employees"""
        if not data or 'period' not in data:
            return {"error": "Invalid payroll data"}
        
        period = data.get('period')
        employee_ids = data.get('employee_ids', [])
        
        # If no specific employees, process for all
        if not employee_ids:
            employee_ids = [emp["id"] for emp in self.employees]
        
        results = []
        for emp_id in employee_ids:
            employee = self.get_employee_by_id(emp_id)
            if employee:
                # Create employee object
                emp_obj = Employee(
                    employee["id"], 
                    employee["name"], 
                    employee["position"], 
                    employee["base_salary"]
                )
                
                # Calculate salary with bonuses, taxes, etc.
                calculated_salary = self._calculate_employee_salary(emp_obj, period)
                
                # Process the payroll
                payroll_result = self._process_employee_payroll(emp_obj, calculated_salary, period)
                
                results.append({
                    "employee_id": emp_id,
                    "name": employee["name"],
                    "period": period,
                    "gross_salary": calculated_salary["gross"],
                    "net_salary": calculated_salary["net"],
                    "status": payroll_result["status"]
                })
        
        return {"results": results, "status": "completed"}
    
    def _calculate_employee_salary(self, employee, period):
        """Calculate an employee's salary"""
        return self.salary_calculator.calculate(employee, period)
    
    def _process_employee_payroll(self, employee, salary_data, period):
        """Process payroll for a single employee"""
        payroll = Payroll(
            employee.id,
            period,
            salary_data["gross"],
            salary_data["net"],
            salary_data["deductions"]
        )
        return self.payroll_processor.process(payroll)
    
    def adjust_employee_salary(self, data, token=None):
        """Adjust an employee's salary"""
        if not data or 'employee_id' not in data or 'adjustment' not in data:
            return {"error": "Invalid adjustment data"}
        
        employee_id = data.get('employee_id')
        adjustment = data.get('adjustment')
        
        return self._perform_salary_adjustment(employee_id, adjustment, token)
    
    def _perform_salary_adjustment(self, employee_id, adjustment, token=None):
        """First level of nested function calls"""
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            return {"error": "Employee not found"}
        
        # Call to second level
        return self._validate_and_apply_adjustment(employee, adjustment, token)
    
    def _validate_and_apply_adjustment(self, employee, adjustment, token=None):
        """Second level of nested function calls"""
        # Some basic validation
        if adjustment < -50 or adjustment > 50:
            return {"error": "Adjustment percentage must be between -50% and +50%"}
        
        # Call to third level
        return self._calculate_new_salary(employee, adjustment, token)
    
    def _calculate_new_salary(self, employee, adjustment, token=None):
        """Third level of nested function calls"""
        # Calculate the new salary
        current_salary = employee["base_salary"]
        adjustment_amount = current_salary * (adjustment / 100)
        new_salary = current_salary + adjustment_amount
        
        # Call to fourth level
        return self._update_employee_salary(employee, new_salary, token)
    
    def _update_employee_salary(self, employee, new_salary, token=None):
        """Fourth level"""
        import jwt
        from flask import current_app
        
        # Check if token exists
        if not token:
            return {"error": "Access denied"}
        
        try:
            # Decode the token
            from app import auth_service
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user = auth_service.get_user_by_id(data['user_id'])
            
            # Check if user is admin
            # todo add this check back
            if not user or not user.get('is_admin'):
                # return {"error": "Permission denied"}
                print("user is not an admin or user is not set")
                
            # Update the employee's salary
            for i, emp in enumerate(self.employees):
                if emp["id"] == employee["id"]:
                    # Capture the prior salary before mutating the record to ensure correct reporting
                    old_salary = employee["base_salary"]
                    self.employees[i]["base_salary"] = new_salary
                    adjustment_percentage = f"{'+' if new_salary > old_salary else ''}{((new_salary - old_salary) / old_salary * 100):.2f}%"
                    return {
                        "success": True,
                        "employee_id": employee["id"],
                        "name": employee["name"],
                        "old_salary": old_salary,
                        "new_salary": new_salary,
                        "adjustment_percentage": adjustment_percentage
                    }
            
            return {"error": "Failed to update employee salary"}
        except Exception as e:
            return {"error": "Invalid token"}
