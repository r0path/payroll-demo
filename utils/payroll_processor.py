from datetime import datetime

class PayrollProcessor:
    def __init__(self):
        self.processed_payrolls = []
    
    def process(self, payroll):
        """Process a payroll entry"""
        # In a real system, this would handle bank transfers, etc.
        payroll.status = "processed"
        payroll.processed_at = datetime.now()
        
        # Add to processed payrolls
        self.processed_payrolls.append({
            "employee_id": payroll.employee_id,
            "period": payroll.period,
            "gross_amount": payroll.gross_amount,
            "net_amount": payroll.net_amount,
            "status": payroll.status,
            "processed_at": payroll.processed_at
        })
        
        return {
            "status": "success",
            "message": f"Payroll for employee {payroll.employee_id} processed successfully",
            "processed_at": payroll.processed_at
        }
