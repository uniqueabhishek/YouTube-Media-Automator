"""Module for handling SQLite database operations.

This module provides functions to setup the database and record download history.
"""
import sqlite3


def setup_database(db_path="downloads.db"):
    """Initialize the SQLite database and create the history table if needed.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        tuple: (connection, cursor) objects.
    """
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
    """Insert a new download record into the history table.

    Args:
        cursor: SQLite cursor object.
        conn: SQLite connection object.
        url (str): The video URL.
        title (str): The video title.
        path (str): The download file path.
        status (str): The download status (e.g., 'Completed').
    """
    cursor.execute(
        "INSERT INTO history (url, title, path, status) VALUES (?, ?, ?, ?)",
        (url, title, path, status),
    )
    conn.commit()
