"""
app.py
------
Personal Finance Tracker — Flask Web Application
Author: Raashid Shaik

Features:
  - User registration and authentication (hashed passwords)
  - Expense logging with categories and dates
  - Monthly budget setting per category
  - Dashboard with KPIs and spending summaries
  - REST-style API endpoints for data retrieval
  - SQLite database with full schema
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from database import init_db, get_db
from auth import register_user, login_user, login_required
from expenses import add_expense, get_expenses, delete_expense, get_monthly_summary
from budgets import set_budget, get_budgets, get_budget_status

app = Flask(__name__)
app.secret_key = "finance_tracker_secret_key_2024"


# ── Initialize DB on startup ──────────────────────────────────────────────────
with app.app_context():
    init_db()


# =============================================================================
# AUTH ROUTES
# =============================================================================

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        success, message = register_user(username, email, password)
        if success:
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash(message, "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        success, result = login_user(username, password)
        if success:
            session["user_id"]  = result["user_id"]
            session["username"] = result["username"]
            return redirect(url_for("dashboard"))
        else:
            flash(result, "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# =============================================================================
# DASHBOARD
# =============================================================================

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    summary = get_monthly_summary(user_id)
    budgets = get_budget_status(user_id)
    recent  = get_expenses(user_id, limit=5)

    return render_template("dashboard.html",
                           username=session["username"],
                           summary=summary,
                           budgets=budgets,
                           recent_expenses=recent)


# =============================================================================
# EXPENSES
# =============================================================================

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    user_id = session["user_id"]

    if request.method == "POST":
        data = {
            "user_id":     user_id,
            "amount":      request.form.get("amount"),
            "category":    request.form.get("category"),
            "description": request.form.get("description", ""),
            "date":        request.form.get("date"),
        }
        success, message = add_expense(data)
        flash(message, "success" if success else "error")

    all_expenses = get_expenses(user_id)
    return render_template("expenses.html", expenses=all_expenses)


@app.route("/expenses/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense_route(expense_id):
    success, message = delete_expense(expense_id, session["user_id"])
    flash(message, "success" if success else "error")
    return redirect(url_for("expenses"))


# =============================================================================
# BUDGETS
# =============================================================================

@app.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets():
    user_id = session["user_id"]

    if request.method == "POST":
        data = {
            "user_id":  user_id,
            "category": request.form.get("category"),
            "amount":   request.form.get("amount"),
            "month":    request.form.get("month"),
            "year":     request.form.get("year"),
        }
        success, message = set_budget(data)
        flash(message, "success" if success else "error")

    budget_status = get_budget_status(user_id)
    return render_template("budgets.html", budgets=budget_status)


# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@app.route("/api/expenses", methods=["GET"])
@login_required
def api_expenses():
    """GET /api/expenses — Returns all expenses for current user as JSON."""
    user_id  = session["user_id"]
    month    = request.args.get("month", type=int)
    year     = request.args.get("year", type=int)
    category = request.args.get("category")

    expenses = get_expenses(user_id, month=month, year=year, category=category)
    return jsonify({"status": "success", "count": len(expenses), "data": expenses})


@app.route("/api/summary", methods=["GET"])
@login_required
def api_summary():
    """GET /api/summary — Returns monthly spending summary as JSON."""
    user_id = session["user_id"]
    summary = get_monthly_summary(user_id)
    return jsonify({"status": "success", "data": summary})


@app.route("/api/budgets", methods=["GET"])
@login_required
def api_budgets():
    """GET /api/budgets — Returns budget vs actual status as JSON."""
    user_id = session["user_id"]
    budgets = get_budget_status(user_id)
    return jsonify({"status": "success", "data": budgets})


@app.route("/api/expenses", methods=["POST"])
@login_required
def api_add_expense():
    """POST /api/expenses — Add a new expense via JSON body."""
    user_id = session["user_id"]
    body = request.get_json()

    if not body:
        return jsonify({"status": "error", "message": "No JSON body provided"}), 400

    data = {
        "user_id":     user_id,
        "amount":      body.get("amount"),
        "category":    body.get("category"),
        "description": body.get("description", ""),
        "date":        body.get("date"),
    }
    success, message = add_expense(data)
    status_code = 201 if success else 400
    return jsonify({"status": "success" if success else "error", "message": message}), status_code


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
