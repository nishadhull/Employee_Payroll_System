from employee import Employee


class HourlyEmployee(Employee):

    def __init__(self, emp_id, name, hours_worked, hourly_rate):
        super().__init__(emp_id, name)

        self.hours_worked = hours_worked
        self.hourly_rate = hourly_rate

    def calculate_pay(self):

        regular_hours = min(self.hours_worked, 160)

        overtime_hours = max(0, self.hours_worked - 160)

        regular_pay = regular_hours * self.hourly_rate

        overtime_pay = overtime_hours * self.hourly_rate * 1.5

        return regular_pay + overtime_pay