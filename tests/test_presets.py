import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from src.presets.presets import CLI_SENTINEL, _parse_extra, app

runner = CliRunner()

SAMPLE_PRESETS = {
    "add-pioneer": {
        "cmd": "expenses add",
        "flags": {
            "--credit": "pioneer",
            "--tag": "$cli",
            "--amount": "$cli",
        },
    },
    "list-food": {
        "cmd": "expenses list",
        "flags": {
            "--tag": "food",
        },
    },
}


@pytest.fixture(autouse=True)
def preset_file(tmp_path, monkeypatch):
    p = tmp_path / "presets.json"
    p.write_text(json.dumps(SAMPLE_PRESETS))
    monkeypatch.setattr("src.presets.presets.PRESETS_FILE", p)
    return p


# --- _parse_extra unit tests ---


def test_parse_extra_basic():
    assert _parse_extra(["--tag", "food", "--amount", "50"]) == {
        "--tag": "food",
        "--amount": "50",
    }


def test_parse_extra_empty():
    assert _parse_extra([]) == {}


def test_parse_extra_single_pair():
    assert _parse_extra(["--credit", "pioneer"]) == {"--credit": "pioneer"}


# --- run: error cases ---


def test_run_unknown_preset():
    result = runner.invoke(app, ["run", "nonexistent"])
    assert result.exit_code != 0
    assert "Unknown preset" in result.output
    assert "add-pioneer" in result.output


def test_run_missing_cli_flag():
    result = runner.invoke(app, ["run", "add-pioneer", "--tag", "food"])
    assert result.exit_code != 0
    assert "Missing required flags" in result.output
    assert "--amount" in result.output


def test_run_flag_missing_value():
    result = runner.invoke(app, ["run", "add-pioneer", "--tag"])
    assert result.exit_code != 0
    assert "requires a value" in result.output


def test_run_unexpected_positional_token():
    result = runner.invoke(app, ["run", "add-pioneer", "notaflag", "value"])
    assert result.exit_code != 0
    assert "Unexpected token" in result.output


def test_run_missing_presets_file(monkeypatch, tmp_path):
    monkeypatch.setattr("src.presets.presets.PRESETS_FILE", tmp_path / "missing.json")
    result = runner.invoke(app, ["run", "add-pioneer"])
    assert result.exit_code != 0
    assert "not found" in result.output


# --- run: happy path ---


def test_run_builds_correct_args():
    with patch("main.app") as mock_app:
        runner.invoke(app, ["run", "add-pioneer", "--tag", "food", "--amount", "50.00"])
    mock_app.assert_called_once_with(
        [
            "expenses",
            "add",
            "--credit",
            "pioneer",
            "--tag",
            "food",
            "--amount",
            "50.00",
        ],
        standalone_mode=True,
    )


def test_run_no_cli_flags_needed():
    with patch("main.app") as mock_app:
        runner.invoke(app, ["run", "list-food"])
    mock_app.assert_called_once_with(
        ["expenses", "list", "--tag", "food"],
        standalone_mode=True,
    )


def test_run_cli_overrides_hardcoded_flag():
    with patch("main.app") as mock_app:
        runner.invoke(
            app,
            [
                "run",
                "add-pioneer",
                "--tag",
                "food",
                "--amount",
                "50.00",
                "--credit",
                "amex",
            ],
        )
    args = mock_app.call_args[0][0]
    credit_idx = args.index("--credit")
    assert args[credit_idx + 1] == "amex"


def test_run_extra_flags_passed_through():
    with patch("main.app") as mock_app:
        runner.invoke(
            app,
            [
                "run",
                "add-pioneer",
                "--tag",
                "food",
                "--amount",
                "50.00",
                "--note",
                "lunch",
            ],
        )
    args = mock_app.call_args[0][0]
    assert "--note" in args
    assert args[args.index("--note") + 1] == "lunch"


# --- list ---


def test_list_shows_all_presets():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "add-pioneer" in result.output
    assert "list-food" in result.output


def test_list_shows_fixed_flags():
    result = runner.invoke(app, ["list"])
    assert "--credit = pioneer" in result.output
    assert "--tag = food" in result.output


def test_list_shows_required_cli_flags():
    result = runner.invoke(app, ["list"])
    assert "--tag" in result.output
    assert "--amount" in result.output


def test_list_empty_presets(monkeypatch, tmp_path):
    empty = tmp_path / "empty.json"
    empty.write_text("{}")
    monkeypatch.setattr("src.presets.presets.PRESETS_FILE", empty)
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No presets defined" in result.output


def test_list_missing_presets_file(monkeypatch, tmp_path):
    monkeypatch.setattr("src.presets.presets.PRESETS_FILE", tmp_path / "missing.json")
    result = runner.invoke(app, ["list"])
    assert result.exit_code != 0
    assert "not found" in result.output
