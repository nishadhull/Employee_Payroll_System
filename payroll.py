from payslip import PaySlip


class PayrollService:

    TAX_RATE = 0.10

    def generate_payslip(self, employee):

        # Calculate gross salary
        gross_pay = employee.calculate_pay()

        # Calculate tax
        tax = gross_pay * self.TAX_RATE

        # Calculate net salary
        net_pay = gross_pay - tax

        # Identify employee type
        if employee.__class__.__name__ == "SalariedEmployee":
            emp_type = "Salaried"

        elif employee.__class__.__name__ == "HourlyEmployee":
            emp_type = "Hourly"

        elif employee.__class__.__name__ == "ContractEmployee":
            emp_type = "Contract"

        else:
            emp_type = "Employee"

        # Create payslip
        payslip = PaySlip(
            employee.emp_id,
            employee.name,
            emp_type,
            round(gross_pay, 2),
            round(tax, 2),
            round(net_pay, 2)
        )

        return payslip