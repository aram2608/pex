from typing import Annotated

import typer

from pex import db, format

from ..util import parse_date_range


def list(
    date_from: Annotated[
        str | None, typer.Option("--date-from", help="start of date range")
    ] = None,
    date_to: Annotated[
        str | None, typer.Option("--date-to", help="end of date range")
    ] = None,
    tag: Annotated[str | None, typer.Option(help="filter by tag")] = None,
):
    if date_to and not date_from:
        raise typer.BadParameter("--date-to requires --date-from")

    from_, to = parse_date_range(date_from, date_to)

    with db.get_db() as con:
        expenses = db.get_expenses(con, from_=from_, to=to, tag=tag)
        for exp in expenses:
            dollar = format.cents_to_dollars(exp["amount"])
            print(f"{exp['id']:>4}  {exp['date']}  ${dollar:>8}  {exp['note']}")
