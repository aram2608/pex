from typing import Annotated

import typer


def mortgage(
    principal: Annotated[float, typer.Option(min=0.01)],
    rate: Annotated[float, typer.Option(min=0.0)],
    term: Annotated[int, typer.Option(min=1)],
    down: Annotated[float, typer.Option()] = 0.0,
):
    """Calculate monthly payments and total interest for a fixed-rate mortgage."""
    p = principal - down
    r = rate / 12 / 100
    n = term * 12
    monthly = p * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    total_interest = (monthly * n) - p

    print(f"Loan amount: {p:.2f}")
    print(f"Monthly payment: {monthly:.2f}")
    print(f"Total interest paid: {total_interest:.2f}")
