# Personal Finance Tracker

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

## 📌 Project Overview

A full-stack personal finance web application built with **Python/Flask** and **SQLite**. Users can register, log expenses by category, set monthly budgets, and track their spending through a dashboard with KPIs and budget status indicators.

---

## ✨ Features

- **User authentication** — secure registration and login with hashed passwords
- **Expense tracking** — log expenses with amount, category, description, and date
- **Budget management** — set monthly budgets per category
- **Dashboard KPIs** — total spent, daily average, top category, budget vs. actual
- **REST API endpoints** — JSON responses for all core data operations
- **Data visualization** — spending breakdown by category

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask 3.0 |
| Database | SQLite (via Python sqlite3) |
| Auth | SHA-256 password hashing |
| API | REST-style JSON endpoints |
| Frontend | HTML, CSS, JavaScript |
| Version Control | Git / GitHub |

---

## 📁 Project Structure

```
personal-finance-tracker/
│
├── app.py              # Flask application, routes, API endpoints
├── database.py         # DB initialization, schema, connection management
├── auth.py             # User registration, login, session decorator
├── expenses.py         # Expense CRUD + monthly summary analytics
├── budgets.py          # Budget setting + budget vs. actual tracking
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates (Jinja2)
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── expenses.html
│   └── budgets.html
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/raashidshaik/personal-finance-tracker.git
cd personal-finance-tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/expenses` | Get all expenses (filterable by month, year, category) |
| POST | `/api/expenses` | Add a new expense via JSON |
| GET | `/api/summary` | Get monthly spending summary |
| GET | `/api/budgets` | Get budget vs. actual status |

### Example API Usage

```bash
# Get expenses for January 2025
GET /api/expenses?month=1&year=2025

# Add expense via JSON
POST /api/expenses
Content-Type: application/json
{
  "amount": 45.50,
  "category": "Food & Dining",
  "description": "Grocery run",
  "date": "2025-01-15"
}
```

### Example API Response
```json
{
  "status": "success",
  "count": 12,
  "data": [
    {
      "expense_id": 1,
      "amount": 45.50,
      "category": "Food & Dining",
      "description": "Grocery run",
      "date": "2025-01-15"
    }
  ]
}
```

---

## 🗄️ Database Schema

### `users`
| Column | Type | Notes |
|---|---|---|
| user_id | INTEGER | Primary key |
| username | TEXT | Unique |
| email | TEXT | Unique |
| password | TEXT | SHA-256 hashed |
| created_at | TEXT | Auto timestamp |

### `expenses`
| Column | Type | Notes |
|---|---|---|
| expense_id | INTEGER | Primary key |
| user_id | INTEGER | FK → users |
| amount | REAL | > 0 enforced |
| category | TEXT | Validated against enum |
| description | TEXT | Optional |
| date | TEXT | YYYY-MM-DD |

### `budgets`
| Column | Type | Notes |
|---|---|---|
| budget_id | INTEGER | Primary key |
|  user_id | INTEGER | FK → users |
| category | TEXT | |
| amount | REAL | > 0 enforced |
| month | INTEGER | 1–12 |
| year | INTEGER | |

---

## 📊 Dashboard KPIs

- **Total Spent** — sum of all expenses in current month
- **Daily Average** — total ÷ days elapsed in month
- **Top Category** — highest spending category
- **Budget Status** — per-category: On Track / Warning (>80%) / Over Budget (>100%)

---

## 👤 Author

**Raashid Shaik**
M.S. Management Information Systems — Lamar University (GPA 3.90)
📧 shaikraashid088@gmail.com
🔗 [LinkedIn](https://linkedin.com/in/raashid-shaik-53a3)
🐙 [GitHub](https://github.com/raashidshaik)
