def cents_to_dollars(cents: int) -> str:
    return f"{cents / 100:.2f}"


def dollars_to_cents(dollars: float) -> int:
    return round(dollars * 100)
