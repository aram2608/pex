import json
from pathlib import Path
from typing import Annotated

import typer

PRESETS_FILE = Path("presets.json")
CLI_SENTINEL = "$cli"

app = typer.Typer(help="Run stored preset commands.")


def _load() -> dict[str, str]:
    if not PRESETS_FILE.exists():
        typer.echo(f"presets.json not found at {PRESETS_FILE.resolve()}", err=True)
        raise typer.Exit(1)
    return json.loads(PRESETS_FILE.read_text())


def _parse_extra(extra: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    it = iter(extra)
    for token in it:
        if not token.startswith("--"):
            typer.echo(f"Unexpected token '{token}' — expected --flag value", err=True)
            raise typer.Exit(1)
        try:
            out[token] = next(it)
        except StopIteration:
            typer.echo(f"Flag '{token}' requires a value", err=True)
            raise typer.Exit(1)
    return out


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def run(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="preset name to run")],
):
    """Run a named preset. Pass any $cli flags as extra --flag value pairs."""
    data = _load()

    if name not in data:
        available = ", ".join(data.keys()) or "(none)"
        typer.echo(f"Unknown preset '{name}'. Available: {available}", err=True)
        raise typer.Exit(1)

    preset = data[name]
    cmd_parts: list[str] = preset["cmd"].split()
    flags: dict[str, str] = preset.get("flags", {})

    cli_vals = _parse_extra(ctx.args)

    missing = [f for f, v in flags.items() if v == CLI_SENTINEL and f not in cli_vals]
    if missing:
        typer.echo(f"Missing required flags: {', '.join(missing)}", err=True)
        raise typer.Exit(1)

    args = cmd_parts[:]
    for flag, value in flags.items():
        # CLI always wins, then preset value, $cli already validated above
        args += [flag, cli_vals.pop(flag, None) or value]

    # Pass through any extra flags not mentioned in the preset
    for flag, value in cli_vals.items():
        args += [flag, value]

    from main import app as main_app

    main_app(args, standalone_mode=True)


@app.command(name="list")
def list_presets():
    """List all available presets and the flags they require."""
    data = _load()
    if not data:
        typer.echo("No presets defined.")
        return
    for name, cfg in data.items():
        fixed = {f: v for f, v in cfg.get("flags", {}).items() if v != CLI_SENTINEL}
        cli_flags = [f for f, v in cfg.get("flags", {}).items() if v == CLI_SENTINEL]
        desc = cfg.get("desc") if "desc" in cfg else ""
        typer.echo(f"\n{name}: command = ({cfg['cmd']})")
        typer.echo(desc)
        for f, v in fixed.items():
            typer.echo(f"  {f} = {v}")
        if cli_flags:
            typer.echo(f"  requires: {', '.join(cli_flags)}")
