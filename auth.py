"""
auth.py
-------
User authentication: registration, login, and session protection.
Author: Raashid Shaik
"""

import sqlite3
import hashlib
import os
from functools import wraps
from flask import session, redirect, url_for

DATABASE = "finance_tracker.db"


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt."""
    salt = "finance_tracker_salt_2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()


def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def register_user(username: str, email: str, password: str):
    """
    Register a new user.
    Returns (True, None) on success, (False, error_message) on failure.
    """
    if not username or not email or not password:
        return False, "All fields are required."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if "@" not in email:
        return False, "Invalid email address."

    hashed = hash_password(password)

    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed)
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def login_user(username: str, password: str):
    """
    Authenticate a user.
    Returns (True, user_dict) on success, (False, error_message) on failure.
    """
    if not username or not password:
        return False, "Username and password are required."

    hashed = hash_password(password)

    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT user_id, username FROM users WHERE username = ? AND password = ?",
            (username, hashed)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return True, {"user_id": user["user_id"], "username": user["username"]}
        else:
            return False, "Invalid username or password."
    except Exception as e:
        return False, f"Login failed: {str(e)}"
