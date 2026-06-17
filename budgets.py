"""
budgets.py
----------
Budget setting and budget vs. actual tracking.
Author: Raashid Shaik
"""

import sqlite3
from datetime import datetime

DATABASE = "finance_tracker.db"


def set_budget(data: dict):
    """Set or update a monthly budget for a category."""
    try:
        user_id  = data.get("user_id")
        category = data.get("category", "").strip()
        amount   = float(data.get("amount", 0))
        month    = int(data.get("month", datetime.now().month))
        year     = int(data.get("year", datetime.now().year))

        if amount <= 0:
            return False, "Budget amount must be greater than zero."
        if not category:
            return False, "Category is required."

        conn = sqlite3.connect(DATABASE)
        # INSERT OR REPLACE handles both create and update
        conn.execute("""
            INSERT INTO budgets (user_id, category, amount, month, year)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, category, month, year)
            DO UPDATE SET amount = excluded.amount
        """, (user_id, category, amount, month, year))
        conn.commit()
        conn.close()
        return True, f"Budget of ${amount:.2f} set for {category}."
    except ValueError:
        return False, "Invalid amount."
    except Exception as e:
        return False, f"Failed to set budget: {str(e)}"


def get_budgets(user_id: int, month: int = None, year: int = None):
    """Get all budgets for a user in a given month/year."""
    now   = datetime.now()
    month = month or now.month
    year  = year  or now.year

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT * FROM budgets
        WHERE user_id = ? AND month = ? AND year = ?
        ORDER BY category
    """, (user_id, month, year)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_budget_status(user_id: int, month: int = None, year: int = None):
    """
    Returns budget vs. actual spending per category for the given month.
    Includes % used and over/under budget status.
    """
    now   = datetime.now()
    month = month or now.month
    year  = year  or now.year

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            b.category,
            b.amount                              AS budget_amount,
            COALESCE(SUM(e.amount), 0)            AS spent,
            ROUND(b.amount - COALESCE(SUM(e.amount), 0), 2) AS remaining,
            ROUND(COALESCE(SUM(e.amount), 0) / b.amount * 100, 1) AS pct_used
        FROM budgets b
        LEFT JOIN expenses e
            ON  e.user_id  = b.user_id
            AND e.category = b.category
            AND strftime('%m', e.date) = printf('%02d', b.month)
            AND strftime('%Y', e.date) = CAST(b.year AS TEXT)
        WHERE b.user_id = ? AND b.month = ? AND b.year = ?
        GROUP BY b.category, b.amount
        ORDER BY pct_used DESC
    """, (user_id, month, year)).fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item["status"] = "Over Budget" if item["pct_used"] > 100 else \
                         "Warning"     if item["pct_used"] > 80  else "On Track"
        result.append(item)
    return result
