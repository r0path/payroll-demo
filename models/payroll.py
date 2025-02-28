class Payroll:
    def __init__(self, employee_id, period, gross_amount, net_amount, deductions):
        self.employee_id = employee_id
        self.period = period
        self.gross_amount = gross_amount
        self.net_amount = net_amount
        self.deductions = deductions
        self.status = "pending"
