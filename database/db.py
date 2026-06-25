import sqlite3
import os
from datetime import datetime, timedelta, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "voice_data.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS voice_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            join_time TEXT NOT NULL,
            leave_time TEXT,
            duration_seconds INTEGER,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_join(user_id: int, timestamp: str) -> int:
    conn = get_connection()
    date = timestamp[:10]
    conn.execute(
        "INSERT INTO voice_sessions (user_id, join_time, date) VALUES (?, ?, ?)",
        (user_id, timestamp, date),
    )
    conn.commit()
    session_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return session_id


def log_leave(session_id: int, leave_time: str, duration_seconds: int):
    conn = get_connection()
    conn.execute(
        "UPDATE voice_sessions SET leave_time = ?, duration_seconds = ? WHERE id = ?",
        (leave_time, duration_seconds, session_id),
    )
    conn.commit()
    conn.close()


def get_open_sessions():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, user_id, join_time FROM voice_sessions WHERE leave_time IS NULL"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def close_session(session_id: int, leave_time: str, duration_seconds: int):
    conn = get_connection()
    conn.execute(
        "UPDATE voice_sessions SET leave_time = ?, duration_seconds = ? WHERE id = ?",
        (leave_time, duration_seconds, session_id),
    )
    conn.commit()
    conn.close()


def get_daily_join_counts(user_id: int, days: int = 7):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    conn = get_connection()
    rows = conn.execute(
        """SELECT date, COUNT(*) as count
           FROM voice_sessions
           WHERE user_id = ? AND date >= ?
           GROUP BY date
           ORDER BY date""",
        (user_id, since.strftime("%Y-%m-%d")),
    ).fetchall()
    conn.close()

    result = {}
    for r in rows:
        result[r["date"]] = r["count"]

    all_days = []
    for i in range(days):
        day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        all_days.insert(0, {"date": day, "count": result.get(day, 0)})

    return all_days


def get_daily_durations(user_id: int, days: int = 7):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    conn = get_connection()
    rows = conn.execute(
        """SELECT date, COALESCE(SUM(duration_seconds), 0) as total_seconds
           FROM voice_sessions
           WHERE user_id = ? AND date >= ?
           GROUP BY date
           ORDER BY date""",
        (user_id, since.strftime("%Y-%m-%d")),
    ).fetchall()
    conn.close()

    result = {}
    for r in rows:
        result[r["date"]] = r["total_seconds"]

    all_days = []
    for i in range(days):
        day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        all_days.insert(0, {"date": day, "total_seconds": result.get(day, 0)})

    return all_days
