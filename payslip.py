from dataclasses import dataclass


@dataclass
class PaySlip:

    employee_id: int
    employee_name: str
    employee_type: str
    gross_pay: float
    tax: float
    net_pay: float

    def display_payslip(self):

        print("\n================================")
        print("          EMPLOYEE PAYSLIP")
        print("================================")

        print("Employee ID:", self.employee_id)
        print("Employee Name:", self.employee_name)
        print("Employee Type:", self.employee_type)

        print("--------------------------------")

        print("Gross Salary: Rs.", self.gross_pay)
        print("Tax Deduction: Rs.", self.tax)
        print("Net Salary: Rs.", self.net_pay)

        print("================================")