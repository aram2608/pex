from typing import Annotated

import typer


def mortgage(
    principal: Annotated[float, typer.Option(min=0.01)],
    rate: Annotated[float, typer.Option(min=0.0)],
    term: Annotated[int, typer.Option(min=1)],
    down: Annotated[float, typer.Option()] = 0.0,
):
    """Calculate monthly payments and total interest for a fixed-rate mortgage."""
    pass
