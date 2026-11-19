class InvalidSalaryDataException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def validate_salary(amount):

    if amount <= 0:
        raise InvalidSalaryDataException(
            "Salary must be greater than zero!"
        )


def validate_hours(hours):

    if hours < 0:
        raise InvalidSalaryDataException(
            "Working hours cannot be negative!"
        )


def validate_rate(rate):

    if rate <= 0:
        raise InvalidSalaryDataException(
            "Hourly rate must be greater than zero!"
        )