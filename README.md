# 💼 Employee Payroll Management System

A Python-based Employee Payroll Management System developed to simplify employee management, salary calculation and payslip generation.

This project uses Object-Oriented Programming (OOP) concepts such as inheritance, polymorphism, method overriding and exception handling.

## 📌 Project Overview

The Employee Payroll Management System is a desktop application that helps organisations manage employee records and calculate salaries efficiently.

It supports three types of employees:
- Salaried Employees
- Hourly Employees
- Contract Employees

Each employee type has its own salary calculation method.

## ✨ Features

- Add new employees
- Update employee details
- Delete employee records
- Search employees
- View all employee records
- Automatic payroll calculation
- Different salary calculations for different employee types
- Generate employee payslips
- Export payslips as PDF
- Input validation and exception handling
- SQLite database integration
- User-friendly graphical interface

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Tkinter | Graphical User Interface |
| SQLite | Database management |
| ReportLab | PDF generation |
| OOP | Code structure and reusability |

## 🏗️ Project Structure

```text
Employee_Payroll_System/
│
├── employee.py
├── salaried_employee.py
├── hourly_employee.py
├── contract_employee.py
├── exceptions.py
├── database.py
├── payroll.py
├── payslip.py
├── gui.py
├── main.py
├── README.md
└── .gitignore
```

## 🧠 OOP Concepts Implemented

**1. Inheritance**

SalariedEmployee, HourlyEmployee and ContractEmployee inherit common properties from the Employee base class.

**2. Polymorphism**

Different employee classes implement their own pay calculation methods.

**3. Method Overriding**

Each employee subclass overrides the salary calculation method according to its payment structure.

**4. Exception Handling**

Custom exceptions are used to handle invalid salary data and prevent incorrect payroll calculations.

**5. Encapsulation**

Employee information and payroll operations are organised within classes.

## 💰 Payroll Calculation

**Salaried Employee:**

Receives a fixed salary.

**Hourly Employee:**

Salary is calculated according to hours worked and hourly rate, including overtime.

**Contract Employee:**

Receives an agreed contract amount.

**Net Salary:**

Net Salary = Gross Salary - Tax Deduction

## 🚀 Installation and Execution

**Step 1: Clone the repository**

```bash
git clone https://github.com/nishadhull/Employee_Payroll_System.git
```

**Step 2: Open the project folder**

```bash
cd Employee_Payroll_System
```

**Step 3: Install the required library**

```bash
pip install reportlab
```

**Step 4: Run the application**

```bash
python gui.py
```

## 🎯 Project Objectives

- Automate employee salary calculations.
- Reduce manual payroll errors.
- Maintain employee records systematically.
- Generate professional employee payslips.
- Demonstrate practical implementation of OOP concepts in Python.

## 🔮 Future Enhancements

- Employee login and authentication.
- Attendance management.
- Monthly payroll reports.
- Advanced salary analytics.
- Cloud database integration.

## 👩‍💻 Developer

**Name:** Nisha

**Project:** Employee Payroll Management System

**GitHub:** [nishadhull](https://github.com/nishadhull)

---

## ⭐ Conclusion

The Employee Payroll Management System demonstrates how Python and Object-Oriented Programming can be used to develop a practical payroll management application.

It simplifies employee management, automates salary calculations and generates payslips through an interactive desktop interface.

**Thank you for visiting my project!**
