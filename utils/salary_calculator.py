class SalaryCalculator:
    def __init__(self):
        self.tax_rate = 0.2  # 20% tax rate
        self.bonus_rates = {
            "Developer": 0.1,  # 10% bonus
            "Manager": 0.15,   # 15% bonus
            "Designer": 0.08   # 8% bonus
        }
    
    def calculate(self, employee, period):
        """Calculate salary with bonuses and deductions"""
        # Base salary
        base_salary = employee.base_salary
        
        # Calculate bonus based on position
        bonus_rate = self.bonus_rates.get(employee.position, 0)
        bonus = base_salary * bonus_rate
        
        # Calculate gross salary (base + bonus)
        gross_salary = base_salary + bonus
        
        # Calculate tax
        tax = gross_salary * self.tax_rate
        
        # Calculate net salary
        net_salary = gross_salary - tax
        
        return {
            "gross": gross_salary,
            "net": net_salary,
            "deductions": {
                "tax": tax
            },
            "bonus": bonus
        }
