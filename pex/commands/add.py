from datetime import date
from typing import Annotated, Optional

import typer

from .. import db, format, util


def add(
    tag: Annotated[str, typer.Option(help="expense tag")],
    amount: Annotated[
        float,
        typer.Option(
            help="amount in dollars",
            min=0.01,
        ),
    ],
    note: Annotated[str, typer.Option()] = "No description provided",
    date_: Annotated[Optional[str], typer.Option("--date")] = None,
):
    cents = format.dollars_to_cents(amount)
    day = util.parse_date(date_) if date_ else date.today().isoformat()

    with db.get_db() as con:
        db.add_expense(con, tag, cents, day, note)
    typer.echo(f"Added: {tag}, ${format.cents_to_dollars(cents)}, {day}")
