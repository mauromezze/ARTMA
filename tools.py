from datetime import datetime
import json
import ast
import operator as op
#import sqlite3

from smolagents import Tool


class CurrentDateTimeTool(Tool):
    name = "current_date_time"
    description = "Return the current local date and time."
    inputs = {}
    output_type = "string"

    def forward(self):
        return datetime.now().isoformat(sep=" ", timespec="seconds")


# class SqliteSelectTool(Tool):
#     name = "sqlite_select"
#     description = "Run a SELECT query against a SQLite database and return rows as JSON."
#     inputs = {
#         "db_path": {"type": "string", "description": "Path to the SQLite database file."},
#         "query": {"type": "string", "description": "SELECT query to execute."},
#         "params": {
#             "type": "array",
#             "description": "Optional query parameters for placeholders in the SQL.",
#             "optional": True,
#         },
#     }
#     output_type = "string"

#     def forward(self, db_path, query, params=None):
#         sql = (query or "").strip()
#         if not sql.lower().startswith("select"):
#             return json.dumps({"error": "Only SELECT queries are allowed."})
#         with sqlite3.connect(db_path) as conn:
#             conn.row_factory = sqlite3.Row
#             cursor = conn.execute(sql, params or [])
#             rows = [dict(row) for row in cursor.fetchall()]
#         return json.dumps(rows)


class ReadExcelTool(Tool):
    name = "read_excel"
    description = "Read rows from an Excel file and return them as JSON."
    inputs = {
        "file_path": {"type": "string", "description": "Path to the Excel file."},
        "sheet_name": {
            "type": "string",
            "description": "Optional sheet name or index; defaults to the first sheet.",
            "nullable": True,
        },
        "n_rows": {
            "type": "integer",
            "description": "Optional number of rows to read from the top.",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, file_path, sheet_name=None, n_rows=None):
        try:
            import pandas as pd
        except ImportError:
            return json.dumps(
                {"error": "Missing dependency: install pandas and openpyxl to read Excel files."}
            )
        df = pd.read_excel(file_path, sheet_name=sheet_name or 0, nrows=n_rows)
        return json.dumps(df.to_dict(orient="records"))


class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluate a math expression using +, -, *, /, **, parentheses, and unary +/-."
    inputs = {
        "expression": {"type": "string", "description": "Math expression to evaluate."},
    }
    output_type = "string"

    _operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.USub: op.neg,
        ast.UAdd: op.pos,
    }

    def _eval_node(self, node):
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)
        if isinstance(node, ast.BinOp):
            op_func = self._operators.get(type(node.op))
            if not op_func:
                raise ValueError("Unsupported operator.")
            return op_func(self._eval_node(node.left), self._eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            op_func = self._operators.get(type(node.op))
            if not op_func:
                raise ValueError("Unsupported unary operator.")
            return op_func(self._eval_node(node.operand))
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported expression.")

    def forward(self, expression):
        try:
            parsed = ast.parse(expression, mode="eval")
            value = self._eval_node(parsed)
        except Exception as exc:
            return json.dumps({"error": f"Invalid expression: {exc}"})
        return json.dumps({"result": value})
