import sqlite3
import json
from datetime import datetime

class RouterAgent:
    def __init__(self, db_path="erp_v2.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def log_tool_call(self, agent, tool, input_data, output_data):
        self.conn.execute(
            "INSERT INTO tool_calls (agent, tool_name, input_json, output_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (agent, tool, json.dumps(input_data), json.dumps(output_data), datetime.now().isoformat())
        )
        self.conn.commit()

    def request_approval(self, module, payload):
        self.conn.execute(
            "INSERT INTO approvals (module, payload_json, status, requested_by, created_at) VALUES (?, ?, ?, ?, ?)",
            (module, json.dumps(payload), "pending", "router", datetime.now().isoformat())
        )
        self.conn.commit()

    def route(self, query: str):
        if "invoice" in query.lower():
            return "finance"
        elif "order" in query.lower() or "customer" in query.lower():
            return "sales"
        elif "stock" in query.lower() or "supplier" in query.lower():
            return "inventory"
        else:
            return "analytics"