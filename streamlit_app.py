import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Employee Payroll Management System",
    page_icon="💼",
    layout="wide"
)

DB_NAME = "streamlit_payroll.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
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


create_table()


# ==========================================
# EMPLOYEE DATABASE FUNCTIONS
# ==========================================

def add_employee(employee):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO employees
        (emp_id, name, employee_type, salary, hours, rate, contract_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        employee["emp_id"],
        employee["name"],
        employee["employee_type"],
        employee["salary"],
        employee["hours"],
        employee["rate"],
        employee["contract_amount"]
    ))

    conn.commit()
    conn.close()


def get_all_employees():

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM employees",
        conn
    )

    conn.close()

    return df


def get_employee(emp_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM employees WHERE emp_id = ?",
        (emp_id,)
    )

    employee = cursor.fetchone()

    conn.close()

    return employee


def update_employee(emp_id, employee):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE employees
        SET name = ?,
            employee_type = ?,
            salary = ?,
            hours = ?,
            rate = ?,
            contract_amount = ?
        WHERE emp_id = ?
    """, (
        employee["name"],
        employee["employee_type"],
        employee["salary"],
        employee["hours"],
        employee["rate"],
        employee["contract_amount"],
        emp_id
    ))

    conn.commit()
    conn.close()


def delete_employee(emp_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM employees WHERE emp_id = ?",
        (emp_id,)
    )

    conn.commit()
    conn.close()


# ==========================================
# PAYROLL CALCULATION
# ==========================================

def calculate_payroll(employee):

    emp_type = employee["employee_type"]

    if emp_type == "Salaried":

        gross_salary = employee["salary"]

    elif emp_type == "Hourly":

        hours = employee["hours"]
        rate = employee["rate"]

        regular_hours = min(hours, 160)
        overtime_hours = max(hours - 160, 0)

        gross_salary = (
            regular_hours * rate
            + overtime_hours * rate * 1.5
        )

    elif emp_type == "Contract":

        gross_salary = employee["contract_amount"]

    else:

        gross_salary = 0

    # Demonstration tax rate: 10%
    tax = gross_salary * 0.10

    net_salary = gross_salary - tax

    return gross_salary, tax, net_salary


# ==========================================
# VALIDATION
# ==========================================

def validate_employee(employee):

    if not employee["emp_id"]:
        raise ValueError("Employee ID is required.")

    if not employee["name"]:
        raise ValueError("Employee name is required.")

    emp_type = employee["employee_type"]

    if emp_type == "Salaried":

        if employee["salary"] <= 0:
            raise ValueError("Salary must be greater than zero.")

    elif emp_type == "Hourly":

        if employee["hours"] <= 0:
            raise ValueError("Working hours must be greater than zero.")

        if employee["rate"] <= 0:
            raise ValueError("Hourly rate must be greater than zero.")

    elif emp_type == "Contract":

        if employee["contract_amount"] <= 0:
            raise ValueError("Contract amount must be greater than zero.")

    else:

        raise ValueError("Invalid employee type.")


# ==========================================
# BULK DATASET IMPORT
# ==========================================

def import_employee_dataset(uploaded_file):

    try:

        filename = uploaded_file.name.lower()

        if filename.endswith(".csv"):

            data = pd.read_csv(uploaded_file)

        elif filename.endswith(".xlsx"):

            data = pd.read_excel(uploaded_file)

        else:

            return None, ["Only CSV and XLSX files are supported."]

        required_columns = [
            "Employee ID",
            "Name",
            "Type",
            "Salary",
            "Hours",
            "Rate",
            "Contract Amount"
        ]

        if not all(col in data.columns for col in required_columns):

            return None, [
                "Dataset columns do not match the required format."
            ]

        imported = 0
        errors = []

        conn = get_connection()
        cursor = conn.cursor()

        # Track duplicate IDs within the uploaded file
        seen_ids = set()

        for index, row in data.iterrows():

            try:

                emp_id = str(row["Employee ID"]).strip()
                name = str(row["Name"]).strip()
                emp_type = str(row["Type"]).strip().title()

                if emp_id.lower() in ["", "nan", "none"]:
                    raise ValueError("Employee ID is required.")

                if name.lower() in ["", "nan", "none"]:
                    raise ValueError("Employee name is required.")

                if emp_id in seen_ids:
                    raise ValueError("Duplicate Employee ID in uploaded file.")

                seen_ids.add(emp_id)

                def number(value):
                    if pd.isna(value) or str(value).strip() == "":
                        return 0.0
                    return float(value)

                salary = number(row["Salary"])
                hours = number(row["Hours"])
                rate = number(row["Rate"])
                contract_amount = number(row["Contract Amount"])

                employee = {
                    "emp_id": emp_id,
                    "name": name,
                    "employee_type": emp_type,
                    "salary": salary,
                    "hours": hours,
                    "rate": rate,
                    "contract_amount": contract_amount
                }

                validate_employee(employee)

                cursor.execute(
                    "SELECT emp_id FROM employees WHERE emp_id = ?",
                    (emp_id,)
                )

                if cursor.fetchone():
                    raise ValueError("Employee ID already exists in database.")

                cursor.execute("""
                    INSERT INTO employees
                    (emp_id, name, employee_type, salary, hours, rate, contract_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    emp_id,
                    name,
                    emp_type,
                    salary,
                    hours,
                    rate,
                    contract_amount
                ))

                imported += 1

            except Exception as e:

                errors.append(
                    f"Row {index + 2}: {str(e)}"
                )

        conn.commit()
        conn.close()

        return imported, errors

    except Exception as e:

        return None, [str(e)]


# ==========================================
# PDF PAYSLIP GENERATION
# ==========================================

def generate_payslip_pdf(employee):

    gross, tax, net = calculate_payroll(employee)

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    pdf.setTitle("Employee Payslip")

    pdf.setFont("Helvetica-Bold", 22)

    pdf.drawCentredString(
        width / 2,
        height - 60,
        "EMPLOYEE PAYSLIP"
    )

    pdf.setFont("Helvetica", 11)

    pdf.drawString(50, height - 110, "Employee Payroll Management System")

    pdf.drawString(50, height - 160, f"Employee ID: {employee['emp_id']}")

    pdf.drawString(50, height - 185, f"Employee Name: {employee['name']}")

    pdf.drawString(50, height - 210, f"Employee Type: {employee['employee_type']}")

    pdf.drawString(
        50,
        height - 235,
        f"Date: {datetime.now().strftime('%d-%m-%Y')}"
    )

    pdf.line(50, height - 260, width - 50, height - 260)

    pdf.setFont("Helvetica-Bold", 13)

    pdf.drawString(50, height - 290, "PAYROLL DETAILS")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(50, height - 330, "Gross Salary")

    pdf.drawRightString(width - 60, height - 330, f"Rs. {gross:,.2f}")

    pdf.drawString(50, height - 365, "Tax (10%)")

    pdf.drawRightString(width - 60, height - 365, f"Rs. {tax:,.2f}")

    pdf.line(50, height - 385, width - 50, height - 385)

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(50, height - 420, "Net Salary")

    pdf.drawRightString(width - 60, height - 420, f"Rs. {net:,.2f}")

    pdf.setFont("Helvetica-Oblique", 10)

    pdf.drawCentredString(
        width / 2,
        60,
        "This is a computer-generated payslip."
    )

    pdf.save()

    buffer.seek(0)

    return buffer


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("💼 Employee Payroll")

st.sidebar.write("Management System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Employee",
        "View Employees",
        "Update Employee",
        "Delete Employee",
        "Search Employee",
        "Generate Payslip",
        "Import Dataset"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Developed by Nisha")


# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":

    st.title("📊 Employee Payroll Dashboard")

    employees = get_all_employees()

    total_employees = len(employees)

    salaried_count = 0
    hourly_count = 0
    contract_count = 0

    total_payroll = 0

    for _, row in employees.iterrows():

        employee = row.to_dict()

        gross, tax, net = calculate_payroll(employee)

        total_payroll += net

        if row["employee_type"] == "Salaried":
            salaried_count += 1

        elif row["employee_type"] == "Hourly":
            hourly_count += 1

        elif row["employee_type"] == "Contract":
            contract_count += 1

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Employees", total_employees)

    col2.metric("Total Payroll", f"₹ {total_payroll:,.2f}")

    col3.metric("Salaried Employees", salaried_count)

    col4, col5 = st.columns(2)

    col4.metric("Hourly Employees", hourly_count)

    col5.metric("Contract Employees", contract_count)

    st.markdown("---")

    st.subheader("Recent Employee Records")

    if not employees.empty:

        st.dataframe(
            employees.tail(10),
            use_container_width=True
        )

    else:

        st.info("No employee records found. Add employees to get started.")


# ==========================================
# ADD EMPLOYEE
# ==========================================

elif menu == "Add Employee":

    st.title("➕ Add New Employee")

    with st.form("add_employee_form"):

        emp_id = st.text_input("Employee ID")

        name = st.text_input("Employee Name")

        emp_type = st.selectbox(
            "Employee Type",
            ["Salaried", "Hourly", "Contract"]
        )

        salary = 0.0
        hours = 0.0
        rate = 0.0
        contract_amount = 0.0

        if emp_type == "Salaried":

            salary = st.number_input(
                "Monthly Salary",
                min_value=0.0
            )

        elif emp_type == "Hourly":

            hours = st.number_input(
                "Working Hours",
                min_value=0.0
            )

            rate = st.number_input(
                "Hourly Rate",
                min_value=0.0
            )

        elif emp_type == "Contract":

            contract_amount = st.number_input(
                "Contract Amount",
                min_value=0.0
            )

        submitted = st.form_submit_button("Add Employee")

        if submitted:

            employee = {
                "emp_id": emp_id.strip(),
                "name": name.strip(),
                "employee_type": emp_type,
                "salary": salary,
                "hours": hours,
                "rate": rate,
                "contract_amount": contract_amount
            }

            try:

                validate_employee(employee)

                if get_employee(employee["emp_id"]):

                    st.error("Employee ID already exists.")

                else:

                    add_employee(employee)

                    st.success("Employee added successfully!")

            except Exception as e:

                st.error(str(e))


# ==========================================
# VIEW EMPLOYEES
# ==========================================

elif menu == "View Employees":

    st.title("👥 All Employees")

    employees = get_all_employees()

    if not employees.empty:

        st.dataframe(
            employees,
            use_container_width=True
        )

        csv_data = employees.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Employee Data (CSV)",
            csv_data,
            "employees.csv",
            "text/csv"
        )

    else:

        st.info("No employees available.")


# ==========================================
# UPDATE EMPLOYEE
# ==========================================

elif menu == "Update Employee":

    st.title("✏️ Update Employee")

    employees = get_all_employees()

    if employees.empty:

        st.info("No employees available.")

    else:

        emp_ids = employees["emp_id"].tolist()

        selected_id = st.selectbox(
            "Select Employee ID",
            emp_ids
        )

        employee = get_employee(selected_id)

        if employee:

            (
                old_id,
                old_name,
                old_type,
                old_salary,
                old_hours,
                old_rate,
                old_contract
            ) = employee

            with st.form("update_employee_form"):

                name = st.text_input(
                    "Employee Name",
                    value=old_name
                )

                emp_type = st.selectbox(
                    "Employee Type",
                    ["Salaried", "Hourly", "Contract"],
                    index=["Salaried", "Hourly", "Contract"].index(old_type)
                )

                salary = old_salary
                hours = old_hours
                rate = old_rate
                contract_amount = old_contract

                if emp_type == "Salaried":

                    salary = st.number_input(
                        "Monthly Salary",
                        min_value=0.0,
                        value=float(old_salary)
                    )

                elif emp_type == "Hourly":

                    hours = st.number_input(
                        "Working Hours",
                        min_value=0.0,
                        value=float(old_hours)
                    )

                    rate = st.number_input(
                        "Hourly Rate",
                        min_value=0.0,
                        value=float(old_rate)
                    )

                elif emp_type == "Contract":

                    contract_amount = st.number_input(
                        "Contract Amount",
                        min_value=0.0,
                        value=float(old_contract)
                    )

                submitted = st.form_submit_button("Update Employee")

                if submitted:

                    updated_employee = {
                        "emp_id": old_id,
                        "name": name.strip(),
                        "employee_type": emp_type,
                        "salary": salary,
                        "hours": hours,
                        "rate": rate,
                        "contract_amount": contract_amount
                    }

                    try:

                        validate_employee(updated_employee)

                        update_employee(
                            old_id,
                            updated_employee
                        )

                        st.success("Employee updated successfully!")

                    except Exception as e:

                        st.error(str(e))


# ==========================================
# DELETE EMPLOYEE
# ==========================================

elif menu == "Delete Employee":

    st.title("🗑️ Delete Employee")

    employees = get_all_employees()

    if employees.empty:

        st.info("No employees available.")

    else:

        emp_ids = employees["emp_id"].tolist()

        selected_id = st.selectbox(
            "Select Employee ID to Delete",
            emp_ids
        )

        employee = get_employee(selected_id)

        if employee:

            st.warning(
                f"Are you sure you want to delete {employee[1]}?"
            )

            if st.button("Confirm Delete"):

                delete_employee(selected_id)

                st.success("Employee deleted successfully!")

                st.rerun()


# ==========================================
# SEARCH EMPLOYEE
# ==========================================

elif menu == "Search Employee":

    st.title("🔍 Search Employee")

    search_id = st.text_input("Enter Employee ID")

    if st.button("Search"):

        employee = get_employee(search_id.strip())

        if employee:

            st.success("Employee found!")

            st.write("Employee ID:", employee[0])

            st.write("Name:", employee[1])

            st.write("Employee Type:", employee[2])

            employee_data = {
                "emp_id": employee[0],
                "name": employee[1],
                "employee_type": employee[2],
                "salary": employee[3],
                "hours": employee[4],
                "rate": employee[5],
                "contract_amount": employee[6]
            }

            gross, tax, net = calculate_payroll(employee_data)

            st.write(f"Gross Salary: ₹ {gross:,.2f}")

            st.write(f"Tax: ₹ {tax:,.2f}")

            st.write(f"Net Salary: ₹ {net:,.2f}")

        else:

            st.error("Employee not found.")


# ==========================================
# GENERATE PAYSLIP
# ==========================================

elif menu == "Generate Payslip":

    st.title("🧾 Generate Employee Payslip")

    employees = get_all_employees()

    if employees.empty:

        st.info("No employees available.")

    else:

        emp_ids = employees["emp_id"].tolist()

        selected_id = st.selectbox(
            "Select Employee",
            emp_ids
        )

        employee = get_employee(selected_id)

        if employee:

            employee_data = {
                "emp_id": employee[0],
                "name": employee[1],
                "employee_type": employee[2],
                "salary": employee[3],
                "hours": employee[4],
                "rate": employee[5],
                "contract_amount": employee[6]
            }

            gross, tax, net = calculate_payroll(employee_data)

            st.subheader("Payroll Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric("Gross Salary", f"₹ {gross:,.2f}")

            col2.metric("Tax", f"₹ {tax:,.2f}")

            col3.metric("Net Salary", f"₹ {net:,.2f}")

            pdf_file = generate_payslip_pdf(employee_data)

            st.download_button(
                label="Download Payslip PDF",
                data=pdf_file,
                file_name=f"Payslip_{selected_id}.pdf",
                mime="application/pdf"
            )


# ==========================================
# IMPORT EMPLOYEE DATASET
# ==========================================

elif menu == "Import Dataset":

    st.title("📂 Import Employee Dataset")

    st.write(
        "Upload your complete employee dataset using a CSV or Excel file."
    )

    st.info(
        "Your file must contain: Employee ID, Name, Type, Salary, "
        "Hours, Rate, Contract Amount."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel File",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:

        try:

            if uploaded_file.name.lower().endswith(".csv"):

                preview_data = pd.read_csv(uploaded_file)

            else:

                preview_data = pd.read_excel(uploaded_file)

            st.subheader("Dataset Preview")

            st.dataframe(
                preview_data.head(10),
                use_container_width=True
            )

            st.write(
                f"Total rows in dataset: {len(preview_data)}"
            )

            if st.button("Import All Employees"):

                uploaded_file.seek(0)

                imported, errors = import_employee_dataset(
                    uploaded_file
                )

                if imported is not None:

                    st.success(
                        f"{imported} employees imported successfully!"
                    )

                    if errors:

                        st.warning("Some rows could not be imported:")

                        for error in errors:

                            st.write("•", error)

                    elif imported == 0:

                        st.info("No new employee records were imported.")

                else:

                    st.error("Import failed.")

                    for error in errors:

                        st.write(error)

        except Exception as e:

            st.error(f"Unable to read file: {str(e)}")


# ==========================================
# FOOTER
# ==========================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Employee Payroll Management System | Python + Streamlit + SQLite"
)