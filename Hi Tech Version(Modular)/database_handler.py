import sqlite3


def setup_database(db_path="downloads.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            url TEXT,
            title TEXT,
            path TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn, cursor


def record_history(cursor, conn, url, title, path, status):
    cursor.execute(
        "INSERT INTO history (url, title, path, status) VALUES (?, ?, ?, ?)",
        (url, title, path, status),
    )
    conn.commit()
