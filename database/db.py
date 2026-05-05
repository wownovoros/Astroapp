import sqlite3
from datetime import datetime, timedelta
from threading import Lock
from typing import Optional

DB_PATH = "db.sqlite3"
_LOCK = Lock()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _LOCK:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                birthdate TEXT NOT NULL,
                sign TEXT NOT NULL,
                is_paid INTEGER NOT NULL DEFAULT 0,
                sub_until TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()


def save_user(user_id: int, birthdate: str, sign: str) -> None:
    with _LOCK:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users(user_id, birthdate, sign)
            VALUES(?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                birthdate=excluded.birthdate,
                sign=excluded.sign
            """,
            (user_id, birthdate, sign),
        )
        conn.commit()
        conn.close()


def get_user(user_id: int) -> Optional[sqlite3.Row]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def set_subscription(user_id: int, days: int = 30) -> None:
    expires_at = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    with _LOCK:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE users
            SET is_paid = 1, sub_until = ?
            WHERE user_id = ?
            """,
            (expires_at, user_id),
        )
        conn.commit()
        conn.close()


def subscription_is_active(user_row: Optional[sqlite3.Row]) -> bool:
    if not user_row:
        return False
    if int(user_row["is_paid"]) != 1:
        return False
    sub_until = user_row["sub_until"]
    if not sub_until:
        return False
    return datetime.utcnow() <= datetime.strptime(sub_until, "%Y-%m-%d %H:%M:%S")


def log_event(user_id: int, event: str, metadata: str = "") -> None:
    with _LOCK:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events(user_id, event, metadata) VALUES(?, ?, ?)",
            (user_id, event, metadata),
        )
        conn.commit()
        conn.close()


def get_conversion_stats() -> dict:
    conn = _connect()
    cur = conn.cursor()
    result = {}
    for key in ("start", "birthdate_saved", "view_horoscope", "paywall", "paid"):
        cur.execute("SELECT COUNT(*) AS c FROM events WHERE event = ?", (key,))
        result[key] = cur.fetchone()["c"]
    conn.close()
    return result
