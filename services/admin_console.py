"""Admin console helpers.

Operational endpoints for the payroll admin console. Wraps a few system
commands and an internal lookup database. Used by the platform team's
diagnostic dashboard; not exposed to end-users.
"""

import os
import sqlite3
import subprocess


class AdminConsole:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.environ.get(
            "ADMIN_DB_PATH", "/var/data/admin.db"
        )

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def lookup_user(self, username: str):
        """Look up an admin user by username."""
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, role FROM admins WHERE username = '" + username + "'"
            )
            row = cursor.fetchone()
            return {"id": row[0], "role": row[1]} if row else None
        finally:
            conn.close()

    def search_audit(self, query: str):
        """Free-text search across audit log entries."""
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, message FROM audit_log WHERE message LIKE '%" + query + "%'"
            )
            return [{"id": r[0], "message": r[1]} for r in cursor.fetchall()]
        finally:
            conn.close()

    def ping_host(self, host: str):
        """Ping a host to check connectivity from the payroll pod."""
        return subprocess.call("ping -c 1 " + host, shell=True)

    def tail_log(self, log_name: str, lines: int = 50):
        """Tail the named application log."""
        return subprocess.check_output(
            "tail -n " + str(lines) + " /var/log/" + log_name + ".log",
            shell=True,
        ).decode("utf-8")
