from typing import Annotated

import typer


def loan(
    principal: Annotated[float, typer.Option(min=0.01)],
    rate: Annotated[float, typer.Option(min=0.0)],
    term: Annotated[int, typer.Option(min=1)],
):
    """Calculate monthly payments and total interest for a fixed-rate amortizing loan."""
    pass
