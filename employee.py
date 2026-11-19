class Employee:

    def __init__(self, emp_id, name):
        self.emp_id = emp_id
        self.name = name

    def calculate_pay(self):
        raise NotImplementedError(
            "Subclass must implement calculate_pay()"
        )

    def display_details(self):
        print("Employee ID:", self.emp_id)
        print("Employee Name:", self.name)