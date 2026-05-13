from datetime import date
from typing import Annotated, Optional

import typer

from src import format, util
from src.db import DBManager


def add(
    tag: Annotated[str, typer.Option(help="expense tag")],
    amount: Annotated[float, typer.Option(help="amount in dollars", min=0.01)],
    credit: Annotated[Optional[str], typer.Option(help="card name if paid by credit card")] = None,
    note: Annotated[str, typer.Option()] = "No description provided",
    date_: Annotated[Optional[str], typer.Option("--date")] = None,
):
    """Add a new expense to the tracker. Use --credit <card> if paid by credit card."""
    cents = format.dollars_to_cents(amount)
    day = util.parse_date(date_) if date_ else date.today().isoformat()

    with DBManager() as db:
        expense_id = db.add_expense(tag, cents, day, note, credit)
        if credit:
            db.add_movement(credit, cents, "charge", day, expense_id)

    card_info = f", {credit}" if credit else ""
    typer.echo(f"Added: {tag}, ${format.cents_to_dollars(cents)}, {day}{card_info}")
