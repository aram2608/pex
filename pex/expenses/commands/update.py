from typing import Annotated, Optional

import typer

from pex import util
from pex.db import DBManager


def update(
    id: Annotated[int, typer.Argument(help="expense ID to update")],
    tag: Annotated[Optional[str], typer.Option(help="new tag")] = None,
    amount: Annotated[Optional[float], typer.Option(help="new amount in dollars", min=0.01)] = None,
    note: Annotated[Optional[str], typer.Option(help="new note")] = None,
    date_: Annotated[Optional[str], typer.Option("--date", help="new date")] = None,
    credit: Annotated[Optional[str], typer.Option(help="card name if paid by credit card")] = None,
):
    """Update an expense. All fields can be updated."""
    fields: dict[str, str | int | None] = {"id": id}
    if tag is not None:
        fields["tag"] = tag
    if amount is not None:
        fields["amount"] = round(amount * 100)
    if note is not None:
        fields["note"] = note
    if date_ is not None:
        fields["date"] = util.parse_date(date_)
    if credit is not None:
        fields["card"] = credit

    if len(fields) == 1:
        raise typer.BadParameter("Provide at least one field to update")

    with DBManager() as db:
        db.update_expense(**fields)
    typer.echo(f"Updated expense {id}")
