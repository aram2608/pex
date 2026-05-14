import typer
from dateutil import parser as dateparser
from dateutil.parser import ParserError


def parse_date(s: str) -> str:
    try:
        return dateparser.parse(s).strftime("%Y-%m-%d")
    except ParserError, ValueError:
        raise typer.BadParameter(f"Cannot parse date: '{s}'")


def parse_date_range(
    from_: str | None, to: str | None
) -> tuple[str | None, str | None]:
    f = parse_date(from_) if from_ else None
    t = parse_date(to) if to else None
    if f and t and f > t:
        raise ValueError("--date-from must not be after --date-to")
    return f, t
