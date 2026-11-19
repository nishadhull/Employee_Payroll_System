from salaried_employee import SalariedEmployee
from hourly_employee import HourlyEmployee
from contract_employee import ContractEmployee
from payroll import PayrollService
from database import Database

from exceptions import (
    validate_salary,
    validate_hours,
    validate_rate,
    InvalidSalaryDataException
)


def load_employees(db):

    employees = []

    records = db.get_all_employees()

    for record in records:

        emp_id, name, emp_type, salary, hours, rate = record

        if emp_type == "Salaried":
            emp = SalariedEmployee(emp_id, name, salary)

        elif emp_type == "Hourly":
            emp = HourlyEmployee(emp_id, name, hours, rate)

        elif emp_type == "Contract":
            emp = ContractEmployee(emp_id, name, salary)

        else:
            continue

        employees.append(emp)

    return employees


def main():

    db = Database()
    payroll = PayrollService()

    while True:

        print("\n================================")
        print("      EMPLOYEE PAYROLL SYSTEM")
        print("================================")

        print("1. Add Salaried Employee")
        print("2. Add Hourly Employee")
        print("3. Add Contract Employee")
        print("4. Display All Employees")
        print("5. Search Employee")
        print("6. Generate All Payslips")
        print("7. Exit")

        choice = input("\nEnter your choice: ")

        try:

            if choice in ["1", "2", "3"]:

                emp_id = int(input("Enter Employee ID: "))
                name = input("Enter Employee Name: ").strip()

                if not name:
                    print("Employee name cannot be empty!")
                    continue

                if db.search_employee(emp_id):
                    print("Employee ID already exists!")
                    continue

                if choice == "1":

                    salary = float(input("Enter Monthly Salary: "))

                    validate_salary(salary)

                    emp = SalariedEmployee(emp_id, name, salary)

                    db.add_employee(
                        emp_id, name, "Salaried", salary
                    )

                elif choice == "2":

                    hours = float(input("Enter Hours Worked: "))
                    rate = float(input("Enter Hourly Rate: "))

                    validate_hours(hours)
                    validate_rate(rate)

                    emp = HourlyEmployee(
                        emp_id, name, hours, rate
                    )

                    db.add_employee(
                        emp_id,
                        name,
                        "Hourly",
                        emp.calculate_pay(),
                        hours,
                        rate
                    )

                elif choice == "3":

                    amount = float(input("Enter Contract Amount: "))

                    validate_salary(amount)

                    emp = ContractEmployee(
                        emp_id, name, amount
                    )

                    db.add_employee(
                        emp_id, name, "Contract", amount
                    )

                print("\nEmployee Added Successfully!")

            elif choice == "4":

                employees = load_employees(db)

                if not employees:
                    print("No employees found!")

                for emp in employees:
                    emp.display_details()
                    print("Gross Salary:", emp.calculate_pay())

            elif choice == "5":

                emp_id = int(input("Enter Employee ID to search: "))

                employee = db.search_employee(emp_id)

                if employee:
                    print("\nEmployee Found!")
                    print("ID:", employee[0])
                    print("Name:", employee[1])
                    print("Type:", employee[2])
                    print("Gross Salary:", employee[3])
                else:
                    print("Employee Not Found!")

            elif choice == "6":

                employees = load_employees(db)

                if not employees:
                    print("No employees available!")

                for emp in employees:

                    payslip = payroll.generate_payslip(emp)

                    payslip.display_payslip()

            elif choice == "7":

                print("Thank you for using Employee Payroll System!")
                break

            else:

                print("Invalid choice! Please try again.")

        except InvalidSalaryDataException as e:

            print("Validation Error:", e)

        except ValueError:

            print("Invalid input! Please enter correct values.")

        except Exception as e:

            print("Error:", e)

    db.close()


if __name__ == "__main__":
    main()