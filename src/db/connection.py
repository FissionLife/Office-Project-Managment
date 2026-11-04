import sqlite3
from typing import Generator
from src.config import DB_PATH

def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection configured with Row factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

