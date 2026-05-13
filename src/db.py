import sqlite3

type Where = tuple[str, list[str]]


class DBManager:
    def __init__(self, db_path: str = "./expenses.db"):
        self._db_path = db_path

    def __enter__(self):
        self.con = sqlite3.connect(self._db_path)
        self.con.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type:
            self.con.rollback()
        self.con.close()

    @staticmethod
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

    @staticmethod
    def update_builder(**f):
        sets, binds = [], []
        for col in ("tag", "amount", "note", "date", "card"):
            if col in f:
                sets.append(f"{col} = ?")
                binds.append(f[col])
        if not sets:
            return None
        sql = "UPDATE expenses SET " + ", ".join(sets) + " WHERE id = ?"
        binds.append(f["id"])
        return sql, binds

    def add_expense(
        self, tag: str, amount: int, date: str, note: str, card: str | None = None
    ) -> int | None:
        cur = self.con.execute(
            "INSERT INTO expenses (tag, amount, date, note, card) VALUES (?, ?, ?, ?, ?)",
            (tag, amount, date, note, card),
        )
        self.con.commit()
        return cur.lastrowid

    def add_movement(
        self,
        card: str,
        amount: int,
        direction: str,
        date: str,
        expense_id: int | None = None,
    ):
        _ = self.con.execute(
            "INSERT INTO credit_card_movements (card, amount, direction, date, expense_id) VALUES (?, ?, ?, ?, ?)",
            (card, amount, direction, date, expense_id),
        )
        self.con.commit()

    def get_expenses(self, *, from_=None, to=None, tag=None) -> list:
        where, binds = self.where_builder(from_=from_, to=to, tag=tag)
        return self.con.execute(
            f"SELECT id, date, tag, amount, note, card FROM expenses{where} ORDER BY date DESC",
            binds,
        ).fetchall()

    def get_movements(self, card: str, *, from_=None, to=None) -> list:
        clauses, binds = ["card = ?"], [card]
        if from_:
            clauses.append("date >= ?")
            binds.append(from_)
        if to:
            clauses.append("date <= ?")
            binds.append(to)
        where = " WHERE " + " AND ".join(clauses)
        return self.con.execute(
            f"SELECT id, date, card, amount, direction, expense_id FROM credit_card_movements{where} ORDER BY date ASC",
            binds,
        ).fetchall()

    def get_total(self, *, from_=None, to=None, tag=None) -> int:
        where, binds = self.where_builder(from_=from_, to=to, tag=tag)
        return self.con.execute(
            f"SELECT COALESCE(SUM(amount), 0) FROM expenses{where}", binds
        ).fetchone()[0]

    def get_tags(self, *, from_=None, to=None) -> list[str]:
        where, binds = self.where_builder(from_=from_, to=to)
        return [
            row[0]
            for row in self.con.execute(
                f"SELECT DISTINCT tag FROM expenses{where} ORDER BY tag", binds
            )
        ]

    def update_expense(self, **fields):
        sql, binds = self.update_builder(**fields)
        _ = self.con.execute(sql, binds)
        self.con.commit()

    def initialize(self):
        """Initialize a new expenses database."""
        _ = self.con.executescript("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag TEXT NOT NULL,
            amount INTEGER NOT NULL,
            date TEXT NOT NULL DEFAULT (date('now')),
            note TEXT NOT NULL DEFAULT 'No description provided',
            card TEXT DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS credit_card_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card TEXT NOT NULL,
            amount INTEGER NOT NULL,
            direction TEXT NOT NULL,
            date TEXT NOT NULL DEFAULT (date('now')),
            expense_id INTEGER REFERENCES expenses(id)
        );
        """)
        print("Database initialized")
