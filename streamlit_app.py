import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Employee Payroll Management System",
    page_icon="💼",
    layout="wide"
)

DB_NAME = "streamlit_payroll.db"
TAX_RATE = 0.10
REGULAR_HOURS = 160
OVERTIME_MULTIPLIER = 1.5


# ==========================================
# CUSTOM EXCEPTION
# ==========================================

class InvalidSalaryDataException(Exception):
    pass


def validate_salary(amount):
    if amount <= 0:
        raise InvalidSalaryDataException(
            "Salary must be greater than zero."
        )


# ==========================================
# EMPLOYEE BASE CLASS
# ==========================================

class Employee:

    def __init__(self, emp_id, name):
        self.emp_id = emp_id
        self.name = name

    def calculate_pay(self):
        raise NotImplementedError(
            "Subclass must implement calculate_pay()."
        )


# ==========================================
# SALARIED EMPLOYEE
# ==========================================

class SalariedEmployee(Employee):

    def __init__(self, emp_id, name, salary):
        super().__init__(emp_id, name)
        validate_salary(salary)
        self.salary = salary

    def calculate_pay(self):
        return self.salary


# ==========================================
# HOURLY EMPLOYEE
# ==========================================

class HourlyEmployee(Employee):

    def __init__(self, emp_id, name, hours, rate):
        super().__init__(emp_id, name)

        if hours <= 0:
            raise InvalidSalaryDataException(
                "Hours must be greater than zero."
            )

        validate_salary(rate)

        self.hours = hours
        self.rate = rate

    def calculate_pay(self):

        regular = min(self.hours, REGULAR_HOURS)

        overtime = max(
            0, self.hours - REGULAR_HOURS
        )

        regular_pay = regular * self.rate

        overtime_pay = (
            overtime * self.rate * OVERTIME_MULTIPLIER
        )

        return regular_pay + overtime_pay


# ==========================================
# CONTRACT EMPLOYEE
# ==========================================

class ContractEmployee(Employee):

    def __init__(self, emp_id, name, amount):
        super().__init__(emp_id, name)
        validate_salary(amount)
        self.amount = amount

    def calculate_pay(self):
        return self.amount


# ==========================================
# DATABASE
# ==========================================

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_database():

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (

            emp_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            employee_type TEXT NOT NULL,
            salary REAL DEFAULT 0,
            hours REAL DEFAULT 0,
            rate REAL DEFAULT 0,
            contract_amount REAL DEFAULT 0

        )
    """)

    conn.commit()
    conn.close()


def get_all_employees():

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM employees ORDER BY emp_id",
        conn
    )

    conn.close()

    return df


def add_employee(emp):

    conn = get_connection()

    conn.execute("""
        INSERT INTO employees
        (emp_id, name, employee_type, salary,
         hours, rate, contract_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        emp["emp_id"],
        emp["name"],
        emp["employee_type"],
        emp["salary"],
        emp["hours"],
        emp["rate"],
        emp["contract_amount"]
    ))

    conn.commit()
    conn.close()


def update_employee(emp):

    conn = get_connection()

    conn.execute("""
        UPDATE employees
        SET name=?,
            employee_type=?,
            salary=?,
            hours=?,
            rate=?,
            contract_amount=?
        WHERE emp_id=?
    """, (
        emp["name"],
        emp["employee_type"],
        emp["salary"],
        emp["hours"],
        emp["rate"],
        emp["contract_amount"],
        emp["emp_id"]
    ))

    conn.commit()
    conn.close()


def delete_employee(emp_id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM employees WHERE emp_id=?",
        (emp_id,)
    )

    conn.commit()
    conn.close()


# ==========================================
# PAYROLL CALCULATION
# ==========================================

def create_employee(row):

    if row["employee_type"] == "Salaried":

        return SalariedEmployee(
            row["emp_id"],
            row["name"],
            row["salary"]
        )

    elif row["employee_type"] == "Hourly":

        return HourlyEmployee(
            row["emp_id"],
            row["name"],
            row["hours"],
            row["rate"]
        )

    elif row["employee_type"] == "Contract":

        return ContractEmployee(
            row["emp_id"],
            row["name"],
            row["contract_amount"]
        )

    raise ValueError("Unknown employee type")


def calculate_payroll(row):

    employee = create_employee(row)

    gross = employee.calculate_pay()

    tax = gross * TAX_RATE

    net = gross - tax

    return gross, tax, net


# ==========================================
# PDF PAYSLIP
# ==========================================

def generate_pdf(row):

    gross, tax, net = calculate_payroll(row)

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>EMPLOYEE PAYSLIP</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 30))

    details = [
        ["Employee ID", row["emp_id"]],
        ["Employee Name", row["name"]],
        ["Employee Type", row["employee_type"]],
        ["Gross Salary", f"Rs. {gross:,.2f}"],
        ["Tax Deduction", f"Rs. {tax:,.2f}"],
        ["Net Salary", f"Rs. {net:,.2f}"]
    ]

    table = Table(
        details,
        colWidths=[180, 230]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.lightblue),

        ("GRID", (0, 0), (-1, -1), 1,
         colors.grey),

        ("PADDING", (0, 0), (-1, -1), 12),

        ("FONTNAME", (0, 0), (-1, -1),
         "Helvetica"),

        ("BACKGROUND", (0, -1), (-1, -1),
         colors.lightgreen)
    ]))

    elements.append(table)

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            "Thank you!",
            styles["Normal"]
        )
    )

    pdf.build(elements)

    buffer.seek(0)

    return buffer


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

create_database()


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #f1f5f9;
}

.main-title {
    background-color: #172554;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    color: white;
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 25px;
}

.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 20px;
}

.stButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("💼 Payroll System")

st.sidebar.markdown("---")

page = st.sidebar.radio(

    "Navigation",

    [
        "Dashboard",
        "Add Employee",
        "Update Employee",
        "Delete Employee",
        "Search Employee",
        "Generate Payslip"
    ]

)

st.sidebar.markdown("---")

st.sidebar.info(
    "Employee Payroll Management System\n\n"
    "Developed by Nisha"
)


# ==========================================
# GET EMPLOYEE DATA
# ==========================================

df = get_all_employees()


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.markdown(
        '<div class="main-title">'
        'EMPLOYEE PAYROLL MANAGEMENT SYSTEM'
        '</div>',
        unsafe_allow_html=True
    )

    total = len(df)

    payroll_total = 0

    if total > 0:

        for _, row in df.iterrows():

            gross, tax, net = calculate_payroll(row)

            payroll_total += gross

    salaried = (
        len(df[df["employee_type"] == "Salaried"])
        if total else 0
    )

    hourly = (
        len(df[df["employee_type"] == "Hourly"])
        if total else 0
    )

    contract = (
        len(df[df["employee_type"] == "Contract"])
        if total else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Employees",
        total
    )

    c2.metric(
        "Total Payroll",
        f"Rs. {payroll_total:,.2f}"
    )

    c3.metric(
        "Total Employee Types",
        f"{salaried} / {hourly} / {contract}",
        help="Salaried / Hourly / Contract"
    )

    st.markdown("### Employee Records")

    if total > 0:

        display = df[[
            "emp_id",
            "name",
            "employee_type"
        ]].copy()

        display.columns = [
            "Employee ID",
            "Employee Name",
            "Employee Type"
        ]

        display["Gross Salary"] = [
            f"Rs. {calculate_payroll(row)[0]:,.2f}"
            for _, row in df.iterrows()
        ]

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No employees found. Add your first employee!"
        )


# ==========================================
# ADD EMPLOYEE
# ==========================================

elif page == "Add Employee":

    st.title("➕ Add New Employee")

    with st.form("add_employee_form"):

        emp_id = st.text_input("Employee ID")

        name = st.text_input("Employee Name")

        employee_type = st.selectbox(
            "Employee Type",
            ["Salaried", "Hourly", "Contract"]
        )

        salary = 0.0
        hours = 0.0
        rate = 0.0
        contract_amount = 0.0

        if employee_type == "Salaried":

            salary = st.number_input(
                "Monthly Salary",
                min_value=0.0,
                value=50000.0
            )

        elif employee_type == "Hourly":

            hours = st.number_input(
                "Hours Worked",
                min_value=0.0,
                value=170.0
            )

            rate = st.number_input(
                "Hourly Rate",
                min_value=0.0,
                value=200.0
            )

        else:

            contract_amount = st.number_input(
                "Contract Amount",
                min_value=0.0,
                value=40000.0
            )

        submit = st.form_submit_button(
            "Save Employee"
        )

        if submit:

            try:

                if not emp_id.strip():
                    raise ValueError(
                        "Employee ID is required."
                    )

                if not name.strip():
                    raise ValueError(
                        "Employee name is required."
                    )

                if employee_type == "Salaried":
                    validate_salary(salary)

                elif employee_type == "Hourly":

                    if hours <= 0:
                        raise ValueError(
                            "Hours must be greater than zero."
                        )

                    validate_salary(rate)

                else:
                    validate_salary(contract_amount)

                emp = {
                    "emp_id": emp_id.strip(),
                    "name": name.strip(),
                    "employee_type": employee_type,
                    "salary": salary,
                    "hours": hours,
                    "rate": rate,
                    "contract_amount": contract_amount
                }

                add_employee(emp)

                st.success(
                    "Employee added successfully!"
                )

                st.rerun()

            except sqlite3.IntegrityError:

                st.error(
                    "Employee ID already exists."
                )

            except Exception as e:

                st.error(str(e))


# ==========================================
# UPDATE EMPLOYEE
# ==========================================

elif page == "Update Employee":

    st.title("✏️ Update Employee")

    if df.empty:

        st.warning("No employee records available.")

    else:

        selected_id = st.selectbox(
            "Select Employee ID",
            df["emp_id"].tolist()
        )

        old = df[
            df["emp_id"] == selected_id
        ].iloc[0]

        types = [
            "Salaried",
            "Hourly",
            "Contract"
        ]

        with st.form("update_form"):

            name = st.text_input(
                "Employee Name",
                value=old["name"]
            )

            employee_type = st.selectbox(
                "Employee Type",
                types,
                index=types.index(old["employee_type"])
            )

            salary = 0.0
            hours = 0.0
            rate = 0.0
            contract_amount = 0.0

            if employee_type == "Salaried":

                salary = st.number_input(
                    "Monthly Salary",
                    min_value=0.0,
                    value=float(old["salary"])
                    if old["employee_type"] == "Salaried"
                    else 50000.0
                )

            elif employee_type == "Hourly":

                hours = st.number_input(
                    "Hours Worked",
                    min_value=0.0,
                    value=float(old["hours"])
                    if old["employee_type"] == "Hourly"
                    else 170.0
                )

                rate = st.number_input(
                    "Hourly Rate",
                    min_value=0.0,
                    value=float(old["rate"])
                    if old["employee_type"] == "Hourly"
                    else 200.0
                )

            else:

                contract_amount = st.number_input(
                    "Contract Amount",
                    min_value=0.0,
                    value=float(old["contract_amount"])
                    if old["employee_type"] == "Contract"
                    else 40000.0
                )

            submit = st.form_submit_button(
                "Update Employee"
            )

            if submit:

                try:

                    if not name.strip():
                        raise ValueError(
                            "Name cannot be empty."
                        )

                    if employee_type == "Salaried":
                        validate_salary(salary)

                    elif employee_type == "Hourly":

                        if hours <= 0:
                            raise ValueError(
                                "Hours must be greater than zero."
                            )

                        validate_salary(rate)

                    else:
                        validate_salary(contract_amount)

                    emp = {
                        "emp_id": selected_id,
                        "name": name.strip(),
                        "employee_type": employee_type,
                        "salary": salary,
                        "hours": hours,
                        "rate": rate,
                        "contract_amount": contract_amount
                    }

                    update_employee(emp)

                    st.success(
                        "Employee updated successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))


# ==========================================
# DELETE EMPLOYEE
# ==========================================

elif page == "Delete Employee":

    st.title("🗑️ Delete Employee")

    if df.empty:

        st.warning("No employees available.")

    else:

        selected_id = st.selectbox(
            "Select Employee ID",
            df["emp_id"].tolist()
        )

        selected = df[
            df["emp_id"] == selected_id
        ].iloc[0]

        st.write(
            "Employee Name:",
            selected["name"]
        )

        st.write(
            "Employee Type:",
            selected["employee_type"]
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this employee."
        )

        if st.button("Delete Employee"):

            if confirm:

                delete_employee(selected_id)

                st.success(
                    "Employee deleted successfully!"
                )

                st.rerun()

            else:

                st.warning(
                    "Please confirm before deleting."
                )


# ==========================================
# SEARCH EMPLOYEE
# ==========================================

elif page == "Search Employee":

    st.title("🔍 Search Employee")

    search = st.text_input(
        "Enter Employee ID or Name"
    )

    if search:

        result = df[
            df["emp_id"].str.contains(
                search,
                case=False,
                na=False
            )
            |
            df["name"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

        if not result.empty:

            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning("Employee not found.")


# ==========================================
# GENERATE PAYSLIP
# ==========================================

elif page == "Generate Payslip":

    st.title("📄 Generate Employee Payslip")

    if df.empty:

        st.warning(
            "Please add employees first."
        )

    else:

        selected_id = st.selectbox(
            "Select Employee",
            df["emp_id"].tolist()
        )

        row = df[
            df["emp_id"] == selected_id
        ].iloc[0]

        gross, tax, net = calculate_payroll(row)

        st.markdown("---")

        st.subheader("Employee Information")

        c1, c2 = st.columns(2)

        c1.write(
            f"**Employee ID:** {row['emp_id']}"
        )

        c2.write(
            f"**Employee Name:** {row['name']}"
        )

        st.write(
            f"**Employee Type:** {row['employee_type']}"
        )

        st.markdown("---")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Gross Salary",
            f"Rs. {gross:,.2f}"
        )

        c2.metric(
            "Tax Deduction",
            f"Rs. {tax:,.2f}"
        )

        c3.metric(
            "Net Salary",
            f"Rs. {net:,.2f}"
        )

        pdf = generate_pdf(row)

        st.download_button(

            label="📥 Download Payslip PDF",

            data=pdf,

            file_name=f"Payslip_{selected_id}.pdf",

            mime="application/pdf"

        )

        st.success(
            "Payslip generated successfully!"
        )


# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.markdown(
    "<center>Employee Payroll Management System | "
    "Developed by Nisha</center>",
    unsafe_allow_html=True
)