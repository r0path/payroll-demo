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
    
    def adjust_employee_salary(self, data):
        """Adjust an employee's salary - VULNERABLE FUNCTION"""
        if not data or 'employee_id' not in data or 'adjustment' not in data:
            return {"error": "Invalid adjustment data"}
        
        employee_id = data.get('employee_id')
        adjustment = data.get('adjustment')
        
        # This function calls deeper functions without proper authorization checks
        return self._perform_salary_adjustment(employee_id, adjustment)
    
    def _perform_salary_adjustment(self, employee_id, adjustment):
        """First level of nested function calls"""
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            return {"error": "Employee not found"}
        
        # Call to second level
        return self._validate_and_apply_adjustment(employee, adjustment)
    
    def _validate_and_apply_adjustment(self, employee, adjustment):
        """Second level of nested function calls"""
        # Some basic validation
        if adjustment < -50 or adjustment > 50:
            return {"error": "Adjustment percentage must be between -50% and +50%"}
        
        # Call to third level
        return self._calculate_new_salary(employee, adjustment)
    
    def _calculate_new_salary(self, employee, adjustment):
        """Third level of nested function calls"""
        # Calculate the new salary
        current_salary = employee["base_salary"]
        adjustment_amount = current_salary * (adjustment / 100)
        new_salary = current_salary + adjustment_amount
        
        # Call to fourth level where the security flaw exists
        return self._update_employee_salary(employee, new_salary)
    
    def _update_employee_salary(self, employee, new_salary):
        """Fourth level - SECURITY FLAW: No token validation here"""
        # This should check authorization but doesn't
        # In a proper implementation, we would validate the JWT token again
        # or pass the authenticated user through the call chain
        
        # Update the employee's salary
        for i, emp in enumerate(self.employees):
            if emp["id"] == employee["id"]:
                self.employees[i]["base_salary"] = new_salary
                return {
                    "success": True,
                    "employee_id": employee["id"],
                    "name": employee["name"],
                    "old_salary": employee["base_salary"],
                    "new_salary": new_salary,
                    "adjustment_percentage": f"{'+' if new_salary > employee['base_salary'] else ''}{((new_salary - employee['base_salary']) / employee['base_salary'] * 100):.2f}%"
                }
        
        return {"error": "Failed to update employee salary"}
