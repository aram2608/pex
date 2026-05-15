import typer

from src.expenses import expenses
from src.interest import interest
from src.presets import presets

app = typer.Typer()

app.add_typer(expenses.app, name="expenses")
app.add_typer(interest.app, name="interest")
app.add_typer(presets.app, name="presets")

if __name__ == "__main__":
    app()
