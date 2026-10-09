import sqlite3

import pytest
from werkzeug.security import check_password_hash

from database import db


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    # Point every get_db() call at a throwaway file instead of the real database
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))


def table_names(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    return {row["name"] for row in rows}


def test_get_db_returns_rows_by_column_name():
    conn = db.get_db()
    row = conn.execute("SELECT 1 AS answer").fetchone()
    assert row["answer"] == 1
    conn.close()


def test_get_db_enables_foreign_keys():
    conn = db.get_db()
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    conn.close()


def test_init_db_creates_tables():
    db.init_db()
    conn = db.get_db()
    assert {"users", "expenses"} <= table_names(conn)
    conn.close()


def test_init_db_can_run_twice():
    db.init_db()
    db.init_db()


def test_seed_db_inserts_demo_data():
    db.init_db()
    db.seed_db()
    conn = db.get_db()
    user = conn.execute("SELECT * FROM users").fetchone()
    assert user["email"] == "demo@spendly.com"
    assert check_password_hash(user["password_hash"], "demo1234")
    count = conn.execute(
        "SELECT COUNT(*) FROM expenses WHERE user_id = ?", (user["id"],)
    ).fetchone()[0]
    assert count == 10
    conn.close()


def test_seed_db_does_not_duplicate():
    db.init_db()
    db.seed_db()
    db.seed_db()
    conn = db.get_db()
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0] == 10
    conn.close()


def test_duplicate_email_rejected():
    db.init_db()
    db.seed_db()
    conn = db.get_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Someone", "demo@spendly.com", "x"),
        )
    conn.close()


def test_expense_requires_existing_user():
    db.init_db()
    conn = db.get_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (999, 100, "Food", "2026-03-01"),
        )
    conn.close()


def test_deleting_user_deletes_their_expenses():
    db.init_db()
    db.seed_db()
    conn = db.get_db()
    conn.execute("DELETE FROM users")
    conn.commit()
    assert conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0] == 0
    conn.close()
