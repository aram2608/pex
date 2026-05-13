from dateutil import parser as dateparser


def parse_date(s: str) -> str:
    return dateparser.parse(s).strftime("%Y-%m-%d")


def parse_date_range(
    from_: str | None, to: str | None
) -> tuple[str | None, str | None]:
    f = parse_date(from_) if from_ else None
    t = parse_date(to) if to else None
    if f and t and f > t:
        raise ValueError("--date-from must not be after --date-to")
    return f, t
