import typer

from src.expenses import expenses
from src.interest import interest

app = typer.Typer()

app.add_typer(expenses.app, name="expenses")
app.add_typer(interest.app, name="interest")

if __name__ == "__main__":
    app()
