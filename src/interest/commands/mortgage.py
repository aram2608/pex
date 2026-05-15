from typing import Annotated

import typer


def mortgage(
    principal: Annotated[
        float, typer.Option(help="loan principal in dollars", min=0.01)
    ],
    rate: Annotated[
        float, typer.Option(help="annual interest rate as a percentage", min=0.0)
    ],
    term: Annotated[int, typer.Option(help="loan term in years", min=1)],
    down: Annotated[float, typer.Option(help="down payment in dollars")] = 0.0,
):
    """Calculate monthly payments and total interest for a fixed-rate mortgage."""
    if down >= principal:
        raise typer.BadParameter("--down must be less than --principal")
    p = principal - down
    r = rate / 12 / 100
    n = term * 12
    monthly = p * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    total_interest = (monthly * n) - p

    typer.echo(f"Loan amount: {p:.2f}")
    typer.echo(f"Monthly payment: {monthly:.2f}")
    typer.echo(f"Total interest paid: {total_interest:.2f}")
