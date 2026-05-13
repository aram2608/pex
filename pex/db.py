import sqlite3
from contextlib import contextmanager


@contextmanager
def get_db():
    con = sqlite3.connect("./expenses.db")
    con.row_factory = sqlite3.Row

    try:
        yield con
    finally:
        con.close()


type Where = tuple[str, list[str]]


def where_builder(**f: str) -> Where:
    clauses, binds = [], []
    if f.get("from_"):
        clauses.append("date >= ?")
        binds.append(f["from_"])
    if f.get("to"):
        clauses.append("date <= ?")
        binds.append(f["to"])
    if f.get("tag"):
        clauses.append("tag = ?")
        binds.append(f["tag"])
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, binds


def update_builder(id: int, **f: str): ...


def add_expense(con, tag: str, amount: int, date: str, note: str):
    con.execute(
        "INSERT INTO expenses (tag, amount, date, note) VALUES (?, ?, ?, ?)",
        (tag, amount, date, note),
    )
    con.commit()


def get_expenses(con, *, from_=None, to=None, tag=None) -> list:
    where, binds = where_builder(from_=from_, to=to, tag=tag)
    return con.execute(
        f"SELECT id, date, tag, amount, note FROM expenses{where} ORDER BY date DESC",
        binds,
    ).fetchall()


def get_total(con, *, from_=None, to=None, tag=None) -> int:
    where, binds = where_builder(from_=from_, to=to, tag=tag)
    return con.execute(
        f"SELECT COALESCE(SUM(amount), 0) FROM expenses{where}", binds
    ).fetchone()[0]


def get_tags(con, *, from_=None, to=None) -> list[str]:
    where, binds = where_builder(from_=from_, to=to)
    return [
        row[0]
        for row in con.execute(
            f"SELECT DISTINCT tag FROM expenses{where} ORDER BY tag", binds
        )
    ]


def update_expense(con, id: int, **fields):
    sql, binds = update_builder(id=id, **fields)
    con.execute(sql, binds)
    con.commit()
