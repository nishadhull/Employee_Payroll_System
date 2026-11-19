from employee import Employee


class SalariedEmployee(Employee):

    def __init__(self, emp_id, name, monthly_salary):

        super().__init__(emp_id, name)

        self.monthly_salary = monthly_salary

    def calculate_pay(self):

        return self.monthly_salary