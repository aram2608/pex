from pex.db import DBManager


def init():
    """Creates a new expenses table in expenses.db"""
    with DBManager() as db:
        db.initialize()
