
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "money.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                group_name TEXT,
                currency TEXT NOT NULL,
                transaction_date TEXT NOT NULL,
                notes TEXT,
                purpose TEXT DEFAULT '',
                necessity TEXT DEFAULT 'Not specified',
                usage_frequency TEXT DEFAULT 'Not specified',
                value_rating INTEGER DEFAULT 0
            )
        """)

        # Safely upgrade databases created by earlier versions.
        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(transactions)"
            ).fetchall()
        }

        new_columns = {
            "purpose": "TEXT DEFAULT ''",
            "necessity": "TEXT DEFAULT 'Not specified'",
            "usage_frequency": "TEXT DEFAULT 'Not specified'",
            "value_rating": "INTEGER DEFAULT 0"
        }

        for column, definition in new_columns.items():
            if column not in existing_columns:
                connection.execute(
                    f"ALTER TABLE transactions ADD COLUMN "
                    f"{column} {definition}"
                )


def save_transaction(transaction):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO transactions (
                title, amount, type, category,
                group_name, currency, transaction_date,
                notes, purpose, necessity,
                usage_frequency, value_rating
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction["title"],
            transaction["amount"],
            transaction["type"],
            transaction["category"],
            transaction["group"],
            transaction["currency"],
            transaction["date"],
            transaction.get("notes", ""),
            transaction.get("purpose", ""),
            transaction.get("necessity", "Not specified"),
            transaction.get("usage_frequency", "Not specified"),
            transaction.get("value_rating", 0)
        ))


def load_transactions():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT * FROM transactions
            ORDER BY transaction_date DESC, id DESC
        """).fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "amount": row["amount"],
            "type": row["type"],
            "category": row["category"],
            "group": row["group_name"],
            "currency": row["currency"],
            "date": row["transaction_date"],
            "notes": row["notes"] or "",
            "purpose": row["purpose"] or "",
            "necessity": row["necessity"] or "Not specified",
            "usage_frequency": row["usage_frequency"] or "Not specified",
            "value_rating": row["value_rating"] or 0
        }
        for row in rows
    ]


def clear_transactions():
    with get_connection() as connection:
        connection.execute("DELETE FROM transactions")
