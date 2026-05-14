
4. amortized.py is not registered

src/interest/interest.py imports credit_card, loan, and mortgage — but not amortized. The new command is
unreachable from the CLI.

# src/interest/interest.py
from .commands import credit_card, loan, mortgage, amortized  # add amortized

app.command()(amortized.amortized)                             # register it

---
Design Issues

5. Schema duplication between db.py and tests/conftest.py

The CREATE TABLE DDL is copy-pasted verbatim into the test fixture. If a column is added to
db.py:initialize(), the test DB will silently run against the old schema, masking real breakage.

The test fixture should call db.initialize() instead:

# tests/conftest.py
@pytest.fixture
def db():
  with DBManager(":memory:") as manager:
      manager.initialize()
      yield manager

6. update_expense doesn't update credit_card_movements

When an expense's amount or card is changed via pex expenses update, the corresponding row in
credit_card_movements is left stale. The balance calculation in credit-card will then be wrong.

Either prevent updating those fields after a charge has been recorded, or cascade the update:

def update_expense(self, **fields):
  result = self.update_builder(**fields)
  if result is None:
      return
  sql, binds = result
  self.con.execute(sql, binds)
  # Sync charge movement if amount changed
  if "amount" in fields:
      self.con.execute(
          "UPDATE credit_card_movements SET amount = ? WHERE expense_id = ? AND direction = 'charge'",
          (fields["amount"], fields["id"]),
      )

7. mortgage.py — no guard for down > principal

p = principal - down produces a negative loan amount if the down payment exceeds the principal. The
amortization formula then returns a negative monthly payment with no warning.

if down >= principal:
  raise typer.BadParameter("--down must be less than --principal")
p = principal - down

---
Style / Consistency

8. Mixed print() and typer.echo()

loan.py, mortgage.py, amortized.py, movements.py (partially), and db.py:initialize() use print().
Everything else uses typer.echo(). In a Typer app, typer.echo() is preferred — it respects -o output
piping, handles encoding, and is capture-friendly in tests. Pick one and stick to it.

9. Missing help= on mortgage options (src/interest/commands/mortgage.py:7-10)

principal, rate, term, and down have no help text. pex interest mortgage --help shows bare option names.
Compare to loan.py which documents all three equivalents.

principal: Annotated[float, typer.Option(help="loan principal in dollars", min=0.01)],
rate: Annotated[float, typer.Option(help="annual interest rate as a percentage", min=0.0)],
term: Annotated[int, typer.Option(help="loan term in years", min=1)],
down: Annotated[float, typer.Option(help="down payment in dollars")] = 0.0,

10. movements command has no docstring and no month/year options

The function body is missing a docstring (shows as blank in --help), and unlike interest credit-card, it
doesn't let you view a past month.

def movements(
  card: Annotated[str, typer.Option(help="the name of the card")],
  month: Annotated[Optional[int], typer.Option(help="billing month (default: current)")] = None,
  year: Annotated[Optional[int], typer.Option(help="billing year (default: current)")] = None,
):
  """List credit card movements for the current (or specified) billing month."""

11. loan.py:13 — output is under-formatted

# Current
print(f"Interest for loan at {rate} for {term}: {interest}")

# Better — consistent with mortgage output
print(f"Principal:           ${principal:,.2f}")
print(f"Rate / term:         {rate}% over {term} year(s)")
print(f"Total interest:      ${interest:,.2f}")
