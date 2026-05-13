from datetime import date
from typing import Annotated, Optional

import typer

from pex import format, util
from pex.db import DBManager


def payment(
    card: Annotated[str, typer.Option(help="card name")],
    amount: Annotated[float, typer.Option(help="payment amount in dollars", min=0.01)],
    note: Annotated[str, typer.Option()] = "No description provided",
    date_: Annotated[Optional[str], typer.Option("--date")] = None,
):
    """Record a credit card payment. Tracks the movement without logging an expense."""
    cents = format.dollars_to_cents(amount)
    day = util.parse_date(date_) if date_ else date.today().isoformat()

    with DBManager() as db:
        db.add_movement(card, cents, "payment", day)

    typer.echo(f"Payment recorded: {card}, ${format.cents_to_dollars(cents)}, {day}")
