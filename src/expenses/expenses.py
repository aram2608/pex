import typer

from .commands import add, init, list, movements, payment, total, update

app = typer.Typer(
    help="Expense tracker. Add expenses to track your monetary discipline."
)
app.command()(add.add)
app.command()(list.list)
app.command()(update.update)
app.command()(total.total)
app.command()(init.init)
app.command()(payment.payment)
app.command()(movements.movements)
