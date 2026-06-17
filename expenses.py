"""
expenses.py
-----------
Expense CRUD operations and monthly summary analytics.
Author: Raashid Shaik
"""

import sqlite3
from datetime import datetime

DATABASE = "finance_tracker.db"

VALID_CATEGORIES = [
    "Food & Dining", "Transportation", "Housing", "Utilities",
    "Healthcare", "Entertainment", "Shopping", "Education",
    "Travel", "Personal Care", "Savings", "Other"
]


def add_expense(data: dict):
    """Add a new expense record."""
    try:
        amount      = float(data.get("amount", 0))
        category    = data.get("category", "").strip()
        description = data.get("description", "").strip()
        date        = data.get("date", "").strip()
        user_id     = data.get("user_id")

        if amount <= 0:
            return False, "Amount must be greater than zero."
        if category not in VALID_CATEGORIES:
            return False, f"Invalid category: {category}"
        if not date:
            return False, "Date is required."

        conn = sqlite3.connect(DATABASE)
        conn.execute(
            """INSERT INTO expenses (user_id, amount, category, description, date)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, amount, category, description, date)
        )
        conn.commit()
        conn.close()
        return True, f"Expense of ${amount:.2f} added to {category}."
    except ValueError:
        return False, "Invalid amount. Please enter a number."
    except Exception as e:
        return False, f"Failed to add expense: {str(e)}"


def get_expenses(user_id: int, limit: int = None, month: int = None,
                 year: int = None, category: str = None):
    """Retrieve expenses with optional filters."""
    query  = "SELECT * FROM expenses WHERE user_id = ?"
    params = [user_id]

    if month:
        query += " AND strftime('%m', date) = ?"
        params.append(f"{month:02d}")
    if year:
        query += " AND strftime('%Y', date) = ?"
        params.append(str(year))
    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY date DESC"

    if limit:
        query += f" LIMIT {limit}"

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_expense(expense_id: int, user_id: int):
    """Delete an expense (only if it belongs to the user)."""
    try:
        conn = sqlite3.connect(DATABASE)
        result = conn.execute(
            "DELETE FROM expenses WHERE expense_id = ? AND user_id = ?",
            (expense_id, user_id)
        )
        conn.commit()
        conn.close()
        if result.rowcount > 0:
            return True, "Expense deleted."
        return False, "Expense not found or unauthorized."
    except Exception as e:
        return False, f"Delete failed: {str(e)}"


def get_monthly_summary(user_id: int):
    """
    Returns spending summary for the current month:
    - Total spent
    - Breakdown by category
    - Daily average
    - Top spending category
    """
    now   = datetime.now()
    month = f"{now.month:02d}"
    year  = str(now.year)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    # Total spent this month
    total = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = ?
          AND strftime('%m', date) = ?
          AND strftime('%Y', date) = ?
    """, (user_id, month, year)).fetchone()["total"]

    # By category
    by_category = conn.execute("""
        SELECT category,
               ROUND(SUM(amount), 2) AS total,
               COUNT(*)              AS count
        FROM expenses
        WHERE user_id = ?
          AND strftime('%m', date) = ?
          AND strftime('%Y', date) = ?
        GROUP BY category
        ORDER BY total DESC
    """, (user_id, month, year)).fetchall()

    # Days elapsed this month
    days_elapsed = now.day
    daily_avg    = round(total / days_elapsed, 2) if days_elapsed > 0 else 0

    conn.close()

    categories = [dict(row) for row in by_category]
    top_category = categories[0]["category"] if categories else "N/A"

    return {
        "month":        now.strftime("%B %Y"),
        "total_spent":  round(total, 2),
        "daily_avg":    daily_avg,
        "top_category": top_category,
        "by_category":  categories,
    }
