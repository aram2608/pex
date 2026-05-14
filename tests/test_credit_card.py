import sqlite3

import pytest

from src.interest.commands.credit_card import _adb_from_movements


def movement(direction: str, amount_cents: int, date: str) -> sqlite3.Row:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE m (direction TEXT, amount INTEGER, date TEXT)")
    con.execute("INSERT INTO m VALUES (?, ?, ?)", (direction, amount_cents, date))
    return con.execute("SELECT * FROM m").fetchone()


def movements(*args) -> list:
    return [movement(*a) for a in args]


def test_single_charge_full_month():
    # $100 charge on day 1 of a 30-day month → ADB = $100
    rows = movements(("charge", 10000, "2024-04-01"))
    assert _adb_from_movements(rows, 2024, 4) == pytest.approx(100.0)


def test_charge_halfway_through_month():
    # $100 charge on day 16 of a 30-day month → contributes 15 days
    rows = movements(("charge", 10000, "2024-04-16"))
    expected = (10000 * 15) / 100 / 30
    assert _adb_from_movements(rows, 2024, 4) == pytest.approx(expected)


def test_payment_reduces_balance():
    # $100 charge day 1, $50 payment day 16 of 30-day month
    # charge contributes 10000 * 30, payment contributes -5000 * 15
    rows = movements(("charge", 10000, "2024-04-01"), ("payment", 5000, "2024-04-16"))
    expected = (10000 * 30 - 5000 * 15) / 100 / 30
    assert _adb_from_movements(rows, 2024, 4) == pytest.approx(expected)


def test_multiple_charges():
    # $100 day 1 + $50 day 11 in a 30-day month
    rows = movements(("charge", 10000, "2024-04-01"), ("charge", 5000, "2024-04-11"))
    expected = (10000 * 30 + 5000 * 20) / 100 / 30
    assert _adb_from_movements(rows, 2024, 4) == pytest.approx(expected)


def test_charge_on_last_day():
    # charge on the last day contributes only 1 day
    rows = movements(("charge", 10000, "2024-04-30"))
    expected = (10000 * 1) / 100 / 30
    assert _adb_from_movements(rows, 2024, 4) == pytest.approx(expected)


def test_february_leap_year():
    rows = movements(("charge", 10000, "2024-02-01"))
    assert _adb_from_movements(rows, 2024, 2) == pytest.approx(100.0)
