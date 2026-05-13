import typer

from .commands import credit_card, loan, mortgage

app = typer.Typer(help="Interest calculator for mortgages, credit cards, and loans.")
app.command()(mortgage.mortgage)
app.command("credit-card")(credit_card.credit_card)
app.command()(loan.loan)
