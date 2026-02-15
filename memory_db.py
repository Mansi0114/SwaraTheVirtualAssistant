import sqlite3
from threading import Lock

DB_FILE = "memory.db"
_lock = Lock()

def _connect():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()

def set_memory(key, value):
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()

def get_memory(key):
    with _lock, _connect() as conn:
        cur = conn.execute(
            "SELECT value FROM memory WHERE key = ?",
            (key,)
        )
        row = cur.fetchone()
        return row[0] if row else None

def clear_memory():
    with _lock, _connect() as conn:
        conn.execute("DELETE FROM memory")
        conn.commit()
