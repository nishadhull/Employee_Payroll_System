from employee import Employee


class ContractEmployee(Employee):

    def __init__(self, emp_id, name, contract_amount):

        super().__init__(emp_id, name)

        self.contract_amount = contract_amount

    def calculate_pay(self):

        return self.contract_amount