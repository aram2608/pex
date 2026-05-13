import pytest

from pex.db import DBManager

SCHEMA = """
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT NOT NULL,
    amount INTEGER NOT NULL,
    date TEXT NOT NULL DEFAULT (date('now')),
    note TEXT NOT NULL DEFAULT 'No description provided',
    card TEXT DEFAULT NULL
);
CREATE TABLE credit_card_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card TEXT NOT NULL,
    amount INTEGER NOT NULL,
    direction TEXT NOT NULL,
    date TEXT NOT NULL DEFAULT (date('now')),
    expense_id INTEGER REFERENCES expenses(id)
);
"""


@pytest.fixture
def db():
    with DBManager(":memory:") as manager:
        manager.con.executescript(SCHEMA)
        yield manager
