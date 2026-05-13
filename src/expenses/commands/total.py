from typing import Annotated

import typer

from src import format
from src.db import DBManager
from src.util import parse_date_range


def total(
    date_from: Annotated[
        str | None, typer.Option("--date-from", help="start of date range")
    ] = None,
    date_to: Annotated[
        str | None, typer.Option("--date-to", help="end of date range")
    ] = None,
    tag: Annotated[str | None, typer.Option(help="filter by tag")] = None,
):
    """
    Prints the sum of all expenses stored in the tracker.
    Can be subest by a specific expense 'tag' or by a date range.
    """
    if date_to and not date_from:
        raise typer.BadParameter("--date-to requires --date-from")

    from_, to = parse_date_range(date_from, date_to)

    with DBManager() as db:
        cents = db.get_total(from_=from_, to=to, tag=tag)
    typer.echo(f"Total: ${format.cents_to_dollars(cents)}")
