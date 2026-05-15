import typer

from src.db import DBManager


def tags():
    with DBManager() as db:
        ts = db.get_tags()
        width = max(len(t) for t in ts) if ts else 0
        for t, c in ts.items():
            typer.echo(f"{t:<{width}}  {c}")
