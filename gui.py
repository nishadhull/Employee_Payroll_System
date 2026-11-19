import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from database import Database
from payroll import PayrollService

from salaried_employee import SalariedEmployee
from hourly_employee import HourlyEmployee
from contract_employee import ContractEmployee

from exceptions import (
    validate_salary,
    validate_hours,
    validate_rate,
    InvalidSalaryDataException
)


class PayrollDashboard:

    def __init__(self, root):

        self.root = root
        self.root.title("Employee Payroll Management System")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        self.root.configure(bg="#eef2f7")

        self.db = Database()
        self.payroll = PayrollService()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

        self.create_header()
        self.create_dashboard()
        self.create_buttons()
        self.create_employee_table()

        self.load_employees()

    # =====================================
    # HEADER
    # =====================================

    def create_header(self):

        header = tk.Frame(
            self.root,
            bg="#172554",
            height=85
        )

        header.pack(fill="x")

        tk.Label(
            header,
            text="EMPLOYEE PAYROLL MANAGEMENT SYSTEM",
            font=("Arial", 20, "bold"),
            bg="#172554",
            fg="white"
        ).pack(pady=23)

    # =====================================
    # DASHBOARD STATISTICS
    # =====================================

    def create_dashboard(self):

        frame = tk.Frame(
            self.root,
            bg="#eef2f7"
        )

        frame.pack(
            fill="x",
            padx=12,
            pady=15
        )

        self.total_label = tk.Label(
            frame,
            text="Total Employees: 0",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#172554",
            pady=20
        )

        self.total_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=4
        )

        self.salary_label = tk.Label(
            frame,
            text="Total Payroll: Rs. 0",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#15803d",
            pady=20
        )

        self.salary_label.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=4
        )

        self.category_label = tk.Label(
            frame,
            text="Salaried: 0 | Hourly: 0 | Contract: 0",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#1d4ed8",
            pady=20
        )

        self.category_label.grid(
            row=0,
            column=2,
            sticky="ew",
            padx=4
        )

        for column in range(3):
            frame.grid_columnconfigure(
                column,
                weight=1
            )

    # =====================================
    # BUTTONS
    # =====================================

    def create_buttons(self):

        frame = tk.Frame(
            self.root,
            bg="#eef2f7"
        )

        frame.pack(pady=8)

        buttons = [
            ("Add Employee", self.add_employee),
            ("Update Employee", self.update_employee),
            ("Delete Employee", self.delete_employee),
            ("Search Employee", self.search_employee),
            ("Refresh Records", self.load_employees),
            ("Generate Payslip", self.generate_payslip),
            ("Export PDF", self.export_pdf)
        ]

        for index, (text, command) in enumerate(buttons):

            tk.Button(
                frame,
                text=text,
                command=command,
                bg="#2563eb",
                fg="white",
                activebackground="#1d4ed8",
                activeforeground="white",
                font=("Arial", 10, "bold"),
                width=20,
                pady=10,
                cursor="hand2",
                relief="raised"
            ).grid(
                row=index // 4,
                column=index % 4,
                padx=5,
                pady=5
            )

    # =====================================
    # EMPLOYEE TABLE
    # =====================================

    def create_employee_table(self):

        frame = tk.Frame(
            self.root,
            bg="white"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        columns = (
            "ID",
            "Name",
            "Type",
            "Salary"
        )

        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=15
        )

        self.table.heading("ID", text="Employee ID")
        self.table.heading("Name", text="Employee Name")
        self.table.heading("Type", text="Employee Type")
        self.table.heading("Salary", text="Gross Salary")

        self.table.column("ID", width=120, anchor="center")
        self.table.column("Name", width=220, anchor="center")
        self.table.column("Type", width=180, anchor="center")
        self.table.column("Salary", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # =====================================
    # LOAD EMPLOYEES
    # =====================================

    def load_employees(self):

        for item in self.table.get_children():
            self.table.delete(item)

        records = self.db.get_all_employees()

        for record in records:

            self.table.insert(
                "",
                "end",
                values=(
                    record[0],
                    record[1],
                    record[2],
                    f"{record[3]:,.2f}"
                )
            )

        self.update_statistics()

    # =====================================
    # UPDATE STATISTICS
    # =====================================

    def update_statistics(self):

        stats = self.db.get_statistics()

        total = stats[0]
        salary = stats[1]

        salaried = stats[2] or 0
        hourly = stats[3] or 0
        contract = stats[4] or 0

        self.total_label.config(
            text=f"Total Employees: {total}"
        )

        self.salary_label.config(
            text=f"Total Payroll: Rs. {salary:,.2f}"
        )

        self.category_label.config(
            text=(
                f"Salaried: {salaried} | "
                f"Hourly: {hourly} | "
                f"Contract: {contract}"
            )
        )

    # =====================================
    # EMPLOYEE FORM
    # =====================================

    def employee_form(self, mode="add", record=None):

        window = tk.Toplevel(self.root)

        window.title("Employee Details")
        window.geometry("420x520")
        window.configure(bg="white")
        window.transient(self.root)
        window.grab_set()

        tk.Label(
            window,
            text="EMPLOYEE DETAILS",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#172554"
        ).pack(pady=15)

        fields = {}

        labels = [
            "Employee ID",
            "Employee Name",
            "Employee Type",
            "Salary / Contract Amount",
            "Hours Worked",
            "Hourly Rate"
        ]

        for label in labels:

            tk.Label(
                window,
                text=label,
                bg="white",
                font=("Arial", 10)
            ).pack(pady=3)

            if label == "Employee Type":

                widget = ttk.Combobox(
                    window,
                    values=[
                        "Salaried",
                        "Hourly",
                        "Contract"
                    ],
                    state="readonly"
                )

            else:

                widget = tk.Entry(
                    window,
                    font=("Arial", 11)
                )

            widget.pack(pady=3, ipadx=5, ipady=3)

            fields[label] = widget

        if mode == "update" and record:

            fields["Employee ID"].insert(
                0, str(record[0])
            )

            fields["Employee ID"].config(
                state="disabled"
            )

            fields["Employee Name"].insert(
                0, record[1]
            )

            fields["Employee Type"].set(record[2])

            if record[2] in ["Salaried", "Contract"]:

                fields["Salary / Contract Amount"].insert(
                    0, str(record[3])
                )

            else:

                fields["Hours Worked"].insert(
                    0, str(record[4])
                )

                fields["Hourly Rate"].insert(
                    0, str(record[5])
                )

        def save_employee():

            try:

                if mode == "update":
                    emp_id = record[0]
                else:
                    emp_id = int(
                        fields["Employee ID"].get()
                    )

                name = fields["Employee Name"].get().strip()

                emp_type = fields["Employee Type"].get()

                if not name or not emp_type:
                    raise ValueError(
                        "Please fill all required fields."
                    )

                if mode == "add" and self.db.search_employee(emp_id):
                    raise ValueError(
                        "Employee ID already exists."
                    )

                salary = 0
                hours = 0
                rate = 0

                if emp_type in ["Salaried", "Contract"]:

                    salary = float(
                        fields["Salary / Contract Amount"].get()
                    )

                    validate_salary(salary)

                elif emp_type == "Hourly":

                    hours = float(
                        fields["Hours Worked"].get()
                    )

                    rate = float(
                        fields["Hourly Rate"].get()
                    )

                    validate_hours(hours)
                    validate_rate(rate)

                    if hours > 300:
                        raise ValueError(
                            "Hours cannot exceed 300."
                        )

                    salary = (
                        min(hours, 160) * rate
                        + max(0, hours - 160) * rate * 1.5
                    )

                if mode == "add":

                    self.db.add_employee(
                        emp_id,
                        name,
                        emp_type,
                        salary,
                        hours,
                        rate
                    )

                    messagebox.showinfo(
                        "Success",
                        "Employee added successfully!"
                    )

                else:

                    self.db.update_employee(
                        emp_id,
                        name,
                        emp_type,
                        salary,
                        hours,
                        rate
                    )

                    messagebox.showinfo(
                        "Success",
                        "Employee updated successfully!"
                    )

                window.destroy()
                self.load_employees()

            except (
                ValueError,
                InvalidSalaryDataException
            ) as error:

                messagebox.showerror(
                    "Validation Error",
                    str(error)
                )

            except Exception as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        tk.Button(
            window,
            text="SAVE EMPLOYEE",
            command=save_employee,
            bg="#16a34a",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=25,
            pady=10
        ).pack(pady=18)

    # =====================================
    # ADD EMPLOYEE
    # =====================================

    def add_employee(self):

        self.employee_form("add")

    # =====================================
    # UPDATE EMPLOYEE
    # =====================================

    def update_employee(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select an employee!"
            )

            return

        emp_id = int(
            self.table.item(
                selected[0],
                "values"
            )[0]
        )

        record = self.db.search_employee(emp_id)

        if record:

            self.employee_form(
                "update",
                record
            )

    # =====================================
    # DELETE EMPLOYEE
    # =====================================

    def delete_employee(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select an employee!"
            )

            return

        emp_id = int(
            self.table.item(
                selected[0],
                "values"
            )[0]
        )

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this employee?"
        )

        if confirm:

            self.db.delete_employee(emp_id)

            messagebox.showinfo(
                "Success",
                "Employee deleted successfully!"
            )

            self.load_employees()

    # =====================================
    # SEARCH EMPLOYEE
    # =====================================

    def search_employee(self):

        emp_id = simpledialog.askinteger(
            "Search Employee",
            "Enter Employee ID:"
        )

        if emp_id is None:
            return

        record = self.db.search_employee(emp_id)

        if record:

            messagebox.showinfo(
                "Employee Found",

                f"Employee ID: {record[0]}\n"
                f"Name: {record[1]}\n"
                f"Type: {record[2]}\n"
                f"Gross Salary: Rs. {record[3]:,.2f}"
            )

        else:

            messagebox.showwarning(
                "Not Found",
                "Employee not found!"
            )

    # =====================================
    # CREATE EMPLOYEE OBJECT
    # =====================================

    def get_employee_object(self, emp_id):

        record = self.db.search_employee(emp_id)

        if not record:
            return None

        emp_id, name, emp_type, salary, hours, rate = record

        if emp_type == "Salaried":

            return SalariedEmployee(
                emp_id, name, salary
            )

        elif emp_type == "Hourly":

            return HourlyEmployee(
                emp_id, name, hours, rate
            )

        elif emp_type == "Contract":

            return ContractEmployee(
                emp_id, name, salary
            )

        return None

    # =====================================
    # GENERATE PAYSLIP
    # =====================================

    def generate_payslip(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select an employee!"
            )

            return

        emp_id = int(
            self.table.item(
                selected[0],
                "values"
            )[0]
        )

        employee = self.get_employee_object(emp_id)

        if employee is None:
            messagebox.showerror(
                "Error",
                "Employee not found!"
            )
            return

        payslip = self.payroll.generate_payslip(employee)

        messagebox.showinfo(
            "Employee Payslip",

            f"EMPLOYEE PAYSLIP\n\n"
            f"Employee ID: {payslip.employee_id}\n"
            f"Employee Name: {payslip.employee_name}\n"
            f"Employee Type: {payslip.employee_type}\n\n"
            f"Gross Salary: Rs. {payslip.gross_pay:,.2f}\n"
            f"Tax Deduction: Rs. {payslip.tax:,.2f}\n"
            f"Net Salary: Rs. {payslip.net_pay:,.2f}"
        )

    # =====================================
    # EXPORT PDF
    # =====================================

    def export_pdf(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select an employee!"
            )

            return

        emp_id = int(
            self.table.item(
                selected[0],
                "values"
            )[0]
        )

        employee = self.get_employee_object(emp_id)

        if employee is None:
            messagebox.showerror(
                "Error",
                "Employee not found!"
            )
            return

        payslip = self.payroll.generate_payslip(employee)

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"Payslip_{emp_id}.pdf"
        )

        if not filename:
            return

        try:

            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas

            pdf = canvas.Canvas(
                filename,
                pagesize=A4
            )

            width, height = A4

            pdf.setTitle("Employee Payslip")

            pdf.setFont("Helvetica-Bold", 22)

            pdf.drawCentredString(
                width / 2,
                height - 80,
                "EMPLOYEE PAYSLIP"
            )

            pdf.line(
                60,
                height - 100,
                width - 60,
                height - 100
            )

            pdf.setFont("Helvetica", 12)

            details = [
                f"Employee ID: {payslip.employee_id}",
                f"Employee Name: {payslip.employee_name}",
                f"Employee Type: {payslip.employee_type}",
                "",
                f"Gross Salary: Rs. {payslip.gross_pay:,.2f}",
                f"Tax Deduction: Rs. {payslip.tax:,.2f}",
                f"Net Salary: Rs. {payslip.net_pay:,.2f}"
            ]

            y = height - 150

            for line in details:

                pdf.drawString(80, y, line)
                y -= 35

            pdf.line(
                60,
                y,
                width - 60,
                y
            )

            pdf.setFont("Helvetica-Bold", 11)

            pdf.drawCentredString(
                width / 2,
                y - 50,
                "Thank you!"
            )

            pdf.save()

            messagebox.showinfo(
                "Success",
                "Payslip PDF generated successfully!"
            )

        except ImportError:

            messagebox.showerror(
                "Missing Library",
                "Run: python -m pip install reportlab"
            )

        except Exception as error:

            messagebox.showerror(
                "PDF Error",
                str(error)
            )

    # =====================================
    # CLOSE APPLICATION
    # =====================================

    def close_app(self):

        self.db.close()
        self.root.destroy()


# =====================================
# MAIN PROGRAM
# =====================================

if __name__ == "__main__":

    root = tk.Tk()

    app = PayrollDashboard(root)

    root.mainloop()