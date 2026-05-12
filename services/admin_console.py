"""Admin console helpers.

Operational endpoints for the payroll admin console. Wraps a few system
commands and an internal lookup database. Used by the platform team's
diagnostic dashboard; not exposed to end-users.
"""

import ipaddress
import os
import re
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
                "SELECT id, role FROM admins WHERE username = ?",
                (username,),
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
                "SELECT id, message FROM audit_log WHERE message LIKE ?",
                (f"%{query}%",),
            )
            return [{"id": r[0], "message": r[1]} for r in cursor.fetchall()]
        finally:
            conn.close()

    def ping_host(self, host: str):
        """Ping a host to check connectivity from the payroll pod.

        Accepts only IPv4/IPv6 addresses or simple hostnames (alphanumeric,
        hyphens, dots) to prevent shell metacharacter injection.
        """
        try:
            ipaddress.ip_address(host)
        except ValueError:
            if not re.fullmatch(r"[a-zA-Z0-9.\-]+", host):
                raise ValueError(f"Invalid host: {host!r}")
        return subprocess.run(["ping", "-c", "1", host], shell=False).returncode

    def tail_log(self, log_name: str, lines: int = 50):
        """Tail the named application log.

        log_name is restricted to alphanumeric/underscore/hyphen characters
        so it cannot be used to traverse paths or inject shell commands.
        """
        if not re.fullmatch(r"[a-zA-Z0-9_\-]+", log_name):
            raise ValueError(f"Invalid log name: {log_name!r}")
        log_path = os.path.join("/var/log", log_name + ".log")
        return subprocess.check_output(
            ["tail", "-n", str(int(lines)), log_path],
            shell=False,
        ).decode("utf-8")
