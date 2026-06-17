"""
database.py
-----------
SQLite database initialization and connection management.
Author: Raashid Shaik
"""

import sqlite3
import os
from flask import g

DATABASE = "finance_tracker.db"


def get_db():
    """Get a database connection, reusing within request context."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Returns rows as dicts
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # ── Users ──────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL UNIQUE,
            email      TEXT NOT NULL UNIQUE,
            password   TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Expenses ───────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            expense_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL    NOT NULL CHECK (amount > 0),
            category    TEXT    NOT NULL,
            description TEXT,
            date        TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # ── Budgets ────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            budget_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            category   TEXT    NOT NULL,
            amount     REAL    NOT NULL CHECK (amount > 0),
            month      INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
            year       INTEGER NOT NULL,
            UNIQUE (user_id, category, month, year),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # ── Indexes for query optimization ─────────────────────────────────────────
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_user  ON expenses(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date  ON expenses(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_cat   ON expenses(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_budgets_user   ON budgets(user_id)")

    conn.commit()
    conn.close()
    print("Database initialized: finance_tracker.db")
