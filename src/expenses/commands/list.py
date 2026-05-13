from typing import Annotated

import typer

from src import format
from src.db import DBManager
from src.util import parse_date_range


def list(
    date_from: Annotated[
        str | None, typer.Option("--date-from", help="start of date range")
    ] = None,
    date_to: Annotated[
        str | None, typer.Option("--date-to", help="end of date range")
    ] = None,
    tag: Annotated[str | None, typer.Option(help="filter by tag")] = None,
):
    """List the expenses stored in the tracker. Can be subset by a date range or expense 'tag'."""
    if date_to and not date_from:
        raise typer.BadParameter("--date-to requires --date-from")

    from_, to = parse_date_range(date_from, date_to)

    with DBManager() as db:
        expenses = db.get_expenses(from_=from_, to=to, tag=tag)
        for exp in expenses:
            dollar = format.cents_to_dollars(exp["amount"])
            card = exp["card"] or "debit"
            print(f"{exp['id']:>4}  {exp['date']}  {card:<10}  ${dollar:>8}  {exp['note']}")
