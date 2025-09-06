# db.py
import sqlite3
from typing import List, Tuple

class SQLiteClient:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # optional: access columns by name
        self.cursor = self.conn.cursor()

    def execute(self, sql: str) -> Tuple[List[str], List[Tuple]]:
        """
        Executes a SELECT query and returns (columns, rows)
        """
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        cols = [description[0] for description in self.cursor.description] if self.cursor.description else []
        return cols, [tuple(row) for row in rows]

    def close(self):
        self.conn.close()
