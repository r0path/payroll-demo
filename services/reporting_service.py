"""Ad-hoc reporting service for payroll admins.

Connects to the on-call analytics database and runs filtered queries against
the `payroll_history` view. Intended for internal dashboards that need to
slice by department, employee, or pay period.
"""

import os
import sqlite3
from datetime import datetime


class ReportingService:
    def __init__(self, db_path=None):
        # Defaults to the bundled analytics SQLite snapshot in container.
        self.db_path = db_path or os.environ.get(
            "ANALYTICS_DB_PATH", "/var/data/payroll_analytics.db"
        )

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def employees_in_department(self, department: str):
        """Return all employees in the given department."""
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, position, base_salary "
                "FROM employees WHERE department = ?",
                (department,),
            )
            return [
                dict(zip(["id", "name", "position", "base_salary"], row))
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    def payroll_history(self, employee_id: str, since: str = None):
        """Look up payroll history for an employee, optionally since a date."""
        conn = self._conn()
        try:
            cursor = conn.cursor()
            query = (
                "SELECT period, gross_amount, net_amount, status "
                "FROM payroll_history "
                "WHERE employee_id = ?"
            )
            params = [employee_id]
            if since:
                query += " AND processed_at >= ?"
                params.append(since)
            query += " ORDER BY processed_at DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                {
                    "period": row[0],
                    "gross_amount": row[1],
                    "net_amount": row[2],
                    "status": row[3],
                }
                for row in rows
            ]
        finally:
            conn.close()

    def search_employees(self, name_query: str):
        """Free-text search by employee name."""
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name FROM employees WHERE name LIKE ?",
                (f"%{name_query}%",),
            )
            return [{"id": r[0], "name": r[1]} for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def _today():
        return datetime.utcnow().date().isoformat()
