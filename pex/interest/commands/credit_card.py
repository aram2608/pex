from calendar import monthrange
from datetime import date
from typing import Annotated, Optional

import typer

from pex.db import DBManager


def _adb_from_movements(
    movements: list,
    year: int,
    month: int,
    starting: float = 0.0,
) -> float:
    _, total_days = monthrange(year, month)
    period_end = date(year, month, total_days)

    total = 0
    for row in movements:
        tx_date = date.fromisoformat(row["date"])
        signed = row["amount"] if row["direction"] == "charge" else -row["amount"]
        total += signed * ((period_end - tx_date).days + 1)

    # starting balance is present for all days, so its ADB contribution equals starting directly
    return (total / 100) / total_days + starting


def credit_card(
    card: Annotated[str, typer.Option(help="card name")],
    apr: Annotated[float, typer.Option(help="annual percentage rate", min=0.0)],
    month: Annotated[
        Optional[int], typer.Option(help="billing month (default: current)")
    ] = None,
    year: Annotated[
        Optional[int], typer.Option(help="billing year (default: current)")
    ] = None,
    starting: Annotated[
        float, typer.Option(help="starting balance for the period (default: 0)")
    ] = 0.0,
):
    """Calculate interest owed for a credit card billing cycle using recorded movements."""
    today = date.today()
    m = month or today.month
    y = year or today.year
    _, total_days = monthrange(y, m)

    from_ = date(y, m, 1).isoformat()
    to = date(y, m, total_days).isoformat()

    with DBManager() as db:
        movements = db.get_movements(card, from_=from_, to=to)

    if not movements:
        typer.echo(f"No movements found for '{card}' in {y}-{m:02d}.")
        raise typer.Exit()

    adb = _adb_from_movements(movements, y, m, starting)
    dpr = (apr / 100) / 365
    interest = dpr * adb * total_days

    typer.echo(f"Card:     {card}  ({y}-{m:02d}, {total_days} days)")
    if starting:
        typer.echo(f"Starting balance:           ${starting:,.2f}")
    typer.echo(f"Average daily balance:      ${adb:,.2f}")
    typer.echo(f"Annual percentage rate:      {apr}%  (DPR: {dpr:.6f})")
    typer.echo(f"Interest: ${interest:,.2f}")
