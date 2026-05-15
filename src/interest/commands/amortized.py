from typing import Annotated

import typer


def amortized(
    principal: Annotated[float, typer.Option(help="the amount of money borrowed")],
    rate: Annotated[float, typer.Option(help="interest rate for loan")],
    term: Annotated[int, typer.Option(help="length of loan")],
    payments: Annotated[int, typer.Option(help="number of payments per year")],
):
    """
    Calculate the interest of an amortized loan.
    Fixed monthly payment formula
    M = P * [r(1+r)^n] / [(1+r)^n - 1]
    """

    # Where P is the principal, r is the periodic interest rate, and n is the total
    # number of payment periods.
    # r = annual rate / payments per year / 100
    # n = term * payments

    r = rate / payments / 100
    n = term * payments
    monthly = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    total_interest = (monthly * n) - principal

    typer.echo(f"Fixed payment: {monthly:.2f}")
    typer.echo(f"Total interest paid: {total_interest:.2f}")
