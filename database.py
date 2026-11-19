import sqlite3


class Database:

    def __init__(self):
        self.conn = sqlite3.connect("payroll.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                emp_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                employee_type TEXT NOT NULL,
                salary REAL NOT NULL,
                hours_worked REAL DEFAULT 0,
                hourly_rate REAL DEFAULT 0
            )
        """)

        self.conn.commit()

    def add_employee(self, emp_id, name, emp_type,
                    salary, hours=0, rate=0):

        self.cursor.execute("""
            INSERT INTO employees
            VALUES (?, ?, ?, ?, ?, ?)
        """, (emp_id, name, emp_type, salary, hours, rate))

        self.conn.commit()

    def get_all_employees(self):

        self.cursor.execute(
            "SELECT * FROM employees ORDER BY emp_id"
        )

        return self.cursor.fetchall()

    def search_employee(self, emp_id):

        self.cursor.execute(
            "SELECT * FROM employees WHERE emp_id = ?",
            (emp_id,)
        )

        return self.cursor.fetchone()

    def update_employee(self, emp_id, name, emp_type,
                        salary, hours=0, rate=0):

        self.cursor.execute("""
            UPDATE employees
            SET name = ?,
                employee_type = ?,
                salary = ?,
                hours_worked = ?,
                hourly_rate = ?
            WHERE emp_id = ?
        """, (name, emp_type, salary, hours, rate, emp_id))

        self.conn.commit()

        return self.cursor.rowcount > 0

    def delete_employee(self, emp_id):

        self.cursor.execute(
            "DELETE FROM employees WHERE emp_id = ?",
            (emp_id,)
        )

        self.conn.commit()

        return self.cursor.rowcount > 0

    def get_statistics(self):

        self.cursor.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(salary), 0),
                SUM(CASE WHEN employee_type = 'Salaried' THEN 1 ELSE 0 END),
                SUM(CASE WHEN employee_type = 'Hourly' THEN 1 ELSE 0 END),
                SUM(CASE WHEN employee_type = 'Contract' THEN 1 ELSE 0 END)
            FROM employees
        """)

        return self.cursor.fetchone()

    def close(self):
        self.conn.close()