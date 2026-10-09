import os
import sqlite3

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expense_tracker.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # SQLite leaves foreign key checks off unless enabled per connection
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount      REAL    NOT NULL CHECK (amount > 0),
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses(user_id, date);
        """
    )
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()

    # Only seed an empty database so repeated runs don't duplicate data
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo1234")),
    )
    user_id = cursor.lastrowid

    expenses = [
        (4500.00, "Bills",         "2026-03-01", "Electricity and internet"),
        (850.00,  "Food",          "2026-03-03", "Groceries"),
        (320.00,  "Transport",     "2026-03-05", "Metro card recharge"),
        (1200.00, "Health",        "2026-03-08", "Pharmacy"),
        (640.00,  "Food",          "2026-03-12", "Dinner with friends"),
        (999.00,  "Entertainment", "2026-03-15", "Concert ticket"),
        (1480.00, "Transport",     "2026-03-18", "Cab rides"),
        (1710.00, "Food",          "2026-03-22", "Weekly groceries"),
        (850.00,  "Health",        "2026-03-25", "Doctor consultation"),
        (2300.00, "Shopping",      "2026-03-28", "New shoes"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        [(user_id, *expense) for expense in expenses],
    )

    conn.commit()
    conn.close()
