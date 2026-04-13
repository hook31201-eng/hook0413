import pyodbc
import os

SERVER   = os.getenv("DB_SERVER",   "163.17.141.61,8000")
DATABASE = os.getenv("DB_NAME",     "gemio10")
USERNAME = os.getenv("DB_USER",     "nutc10")
PASSWORD = os.getenv("DB_PASSWORD", "Nutc@2026")


def _conn_str() -> str:
    return (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "TrustServerCertificate=yes;"
    )


def get_connection():
    return pyodbc.connect(_conn_str())


def get_schema() -> str:
    """Read all tables + columns from SQL Server and return as a text block."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                t.TABLE_NAME,
                c.COLUMN_NAME,
                c.DATA_TYPE
            FROM INFORMATION_SCHEMA.TABLES t
            JOIN INFORMATION_SCHEMA.COLUMNS c
                ON t.TABLE_NAME = c.TABLE_NAME AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
            WHERE t.TABLE_TYPE = 'BASE TABLE'
            ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
        """)
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        return f"[Schema load error: {e}]"

    schema_dict: dict[str, list[str]] = {}
    for table, col, dtype in rows:
        schema_dict.setdefault(table, []).append(f"{col}({dtype})")

    lines = []
    for table, cols in schema_dict.items():
        lines.append(f"TABLE {table}: " + ", ".join(cols))
    return "\n".join(lines)


def get_tables_list() -> list[str]:
    """Return a sorted list of all base-table names."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = [r[0] for r in cursor.fetchall()]
        conn.close()
        return tables
    except Exception:
        return []


def execute_query(sql: str) -> tuple[list[str], list[list[str]]]:
    """Execute a SQL statement and return (columns, rows)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = []
    for row in cursor.fetchall():
        rows.append([("" if v is None else str(v)) for v in row])
    conn.close()
    return columns, rows
