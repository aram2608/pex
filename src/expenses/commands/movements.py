from calendar import monthrange
from datetime import date
from typing import Annotated

import typer

from src.db import DBManager
from src.format import cents_to_dollars


def movements(card: Annotated[str, typer.Option(help="the name of the card")]):
    today: date = date.today()
    m = today.month
    y = today.year
    _, total_days = monthrange(y, m)

    from_ = date(y, m, 1).isoformat()
    to = date(y, m, total_days).isoformat()

    with DBManager() as db:
        movements = db.get_movements(card, from_=from_, to=to)

    if not movements:
        typer.echo(f"No movements found for '{card}' in {y}-{m:02d}.")
        raise typer.Exit()

    for move in movements:
        dol = cents_to_dollars(move["amount"])
        print(f"{move['date']}  {move['direction']:<7}  ${dol:>10}")
