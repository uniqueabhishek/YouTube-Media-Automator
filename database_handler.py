"""Module for handling SQLite database operations.

This module provides a DatabaseManager class to handle SQLite connections
safely using context managers.
"""
import sqlite3

from typing import Optional


class DatabaseManager:
    """Context manager for SQLite database operations."""

    def __init__(self, db_path: str):
        """Initialize with database path.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def __enter__(self):
        """Open database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close database connection and commit if no errors."""
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            self.conn.close()

    def create_table(self):
        """Create the history table if it doesn't exist."""
        if not self.cursor:
            raise RuntimeError("Database connection not open")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                url TEXT,
                title TEXT,
                path TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def record_history(self, url: str, title: str, path: str, status: str):
        """Insert a new download record into the history table.

        Args:
            url (str): The video URL.
            title (str): The video title.
            path (str): The download file path.
            status (str): The download status (e.g., 'Completed').
        """
        if not self.cursor:
            raise RuntimeError("Database connection not open")

        self.cursor.execute(
            "INSERT INTO history (url, title, path, status) VALUES (?, ?, ?, ?)",
            (url, title, path, status),
        )


def init_db(db_path: str):
    """Ensure the database table exists on startup.

    Args:
        db_path (str): Path to the database file.
    """
    with DatabaseManager(db_path) as db:
        db.create_table()
