from typing import Annotated

import typer


def loan(
    principal: Annotated[float, typer.Option(help="principal on the loan", min=0.01)],
    rate: Annotated[float, typer.Option(help="interest rate as a percentage", min=0.0)],
    term: Annotated[int, typer.Option(help="loan term in years", min=1)],
):
    """Calculate simple interest for a loan."""
    interest = principal * (rate / 100) * term
    print(f"Interest for loan at {rate} for {term}: {interest}")
