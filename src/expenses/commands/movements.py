from calendar import monthrange
from datetime import date
from typing import Annotated, Optional

import typer

from src.db import DBManager
from src.format import cents_to_dollars


def movements(
    card: Annotated[str, typer.Option(help="the name of the card")],
    month: Annotated[
        Optional[int], typer.Option(help="billing month (default: current)")
    ] = None,
    year: Annotated[
        Optional[int], typer.Option(help="billing year (default: current)")
    ] = None,
):
    """List credit card movements for the current (or specified) billing month."""
    today: date = date.today()
    m = month or today.month
    y = year or today.year
    _, total_days = monthrange(y, m)

    from_ = date(y, m, 1).isoformat()
    to = date(y, m, total_days).isoformat()

    with DBManager() as db:
        rows = db.get_movements(card, from_=from_, to=to)

    if not rows:
        typer.echo(f"No movements found for '{card}' in {y}-{m:02d}.")
        raise typer.Exit()

    for move in rows:
        dol = cents_to_dollars(move["amount"])
        typer.echo(f"{move['date']}  {move['direction']:<7}  ${dol:>10}")
