import pytest

from src.db import DBManager


def test_add_and_retrieve(db):
    db.add_expense("food", 1000, "2024-01-01", "lunch")
    rows = db.get_expenses()
    assert len(rows) == 1
    assert rows[0]["tag"] == "food"
    assert rows[0]["amount"] == 1000
    assert rows[0]["date"] == "2024-01-01"
    assert rows[0]["note"] == "lunch"
    assert rows[0]["card"] is None


def test_add_expense_with_card(db):
    db.add_expense("food", 1000, "2024-01-01", "lunch", "chase")
    assert db.get_expenses()[0]["card"] == "chase"


def test_add_expense_default_card_is_none(db):
    db.add_expense("food", 1000, "2024-01-01", "lunch")
    assert db.get_expenses()[0]["card"] is None


def test_add_expense_returns_id(db):
    id_ = db.add_expense("food", 1000, "2024-01-01", "lunch")
    assert isinstance(id_, int)
    assert id_ > 0


def test_add_movement_charge(db):
    expense_id = db.add_expense("food", 1000, "2024-01-01", "lunch", "chase")
    db.add_movement("chase", 1000, "charge", "2024-01-01", expense_id)
    movements = db.get_movements("chase")
    assert len(movements) == 1
    assert movements[0]["direction"] == "charge"
    assert movements[0]["amount"] == 1000
    assert movements[0]["expense_id"] == expense_id


def test_add_movement_payment(db):
    db.add_movement("chase", 5000, "payment", "2024-01-15")
    movements = db.get_movements("chase")
    assert len(movements) == 1
    assert movements[0]["direction"] == "payment"
    assert movements[0]["expense_id"] is None


def test_get_movements_filter_by_date(db):
    db.add_movement("chase", 1000, "charge", "2024-01-01")
    db.add_movement("chase", 2000, "charge", "2024-06-01")
    db.add_movement("chase", 5000, "payment", "2024-12-01")
    rows = db.get_movements("chase", from_="2024-05-01", to="2024-07-01")
    assert len(rows) == 1
    assert rows[0]["amount"] == 2000


def test_get_movements_filters_by_card(db):
    db.add_movement("chase", 1000, "charge", "2024-01-01")
    db.add_movement("amex", 2000, "charge", "2024-01-01")
    assert len(db.get_movements("chase")) == 1
    assert len(db.get_movements("amex")) == 1


def test_get_movements_ordered_by_date_asc(db):
    db.add_movement("chase", 1000, "charge", "2024-03-01")
    db.add_movement("chase", 2000, "charge", "2024-01-01")
    dates = [r["date"] for r in db.get_movements("chase")]
    assert dates == sorted(dates)


def test_get_expenses_returns_newest_first(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    db.add_expense("food", 600, "2024-03-01", "b")
    db.add_expense("food", 700, "2024-02-01", "c")
    dates = [r["date"] for r in db.get_expenses()]
    assert dates == sorted(dates, reverse=True)


def test_get_expenses_filter_by_tag(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    db.add_expense("rent", 100000, "2024-01-02", "b")
    rows = db.get_expenses(tag="food")
    assert all(r["tag"] == "food" for r in rows)
    assert len(rows) == 1


def test_get_expenses_filter_by_date_range(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    db.add_expense("food", 600, "2024-06-01", "b")
    db.add_expense("food", 700, "2024-12-01", "c")
    rows = db.get_expenses(from_="2024-02-01", to="2024-11-01")
    assert len(rows) == 1
    assert rows[0]["date"] == "2024-06-01"


def test_get_expenses_empty(db):
    assert db.get_expenses() == []


def test_get_total(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    db.add_expense("food", 1500, "2024-01-02", "b")
    assert db.get_total() == 2000


def test_get_total_empty_returns_zero(db):
    assert db.get_total() == 0


def test_get_total_filter_by_tag(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    db.add_expense("rent", 100000, "2024-01-02", "b")
    assert db.get_total(tag="food") == 500


def test_get_total_filter_by_date_range(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    db.add_expense("food", 999, "2024-06-01", "b")
    assert db.get_total(from_="2024-05-01", to="2024-12-01") == 999


def test_get_tags(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    db.add_expense("rent", 100000, "2024-01-02", "b")
    db.add_expense("food", 300, "2024-01-03", "c")
    assert db.get_tags() == ["food", "rent"]


def test_get_tags_empty(db):
    assert db.get_tags() == []


def test_get_tags_filter_by_date_range(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    db.add_expense("rent", 100000, "2024-06-01", "b")
    assert db.get_tags(from_="2024-05-01") == ["rent"]


def test_update_expense_tag(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    id_ = db.get_expenses()[0]["id"]
    db.update_expense(id=id_, tag="transport")
    assert db.get_expenses()[0]["tag"] == "transport"


def test_update_expense_multiple_fields(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    id_ = db.get_expenses()[0]["id"]
    db.update_expense(id=id_, amount=999, note="updated")
    row = db.get_expenses()[0]
    assert row["amount"] == 999
    assert row["note"] == "updated"


def test_update_expense_card(db):
    db.add_expense("food", 500, "2024-01-01", "a")
    id_ = db.get_expenses()[0]["id"]
    db.update_expense(id=id_, card="chase")
    assert db.get_expenses()[0]["card"] == "chase"


def test_update_expense_no_fields_returns_none(db):
    assert DBManager.update_builder(id=1) is None


def test_where_builder_no_filters():
    clause, binds = DBManager.where_builder()
    assert clause == ""
    assert binds == []


def test_where_builder_all_filters():
    clause, binds = DBManager.where_builder(
        from_="2024-01-01", to="2024-12-31", tag="food"
    )
    assert "date >=" in clause
    assert "date <=" in clause
    assert "tag =" in clause
    assert binds == ["2024-01-01", "2024-12-31", "food"]
