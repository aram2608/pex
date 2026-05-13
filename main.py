import typer

from pex.commands import add, list

app = typer.Typer()
app.command()(add.add)
app.command()(list.list)

if __name__ == "__main__":
    app()
