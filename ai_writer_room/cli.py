"""Command line interface for AI Writer Room v0.1."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console


app = typer.Typer(help="AI Writer Room v0.1 CLI.")
console = Console()


@app.command()
def storyboard(
    premise: str,
    output: Path | None = None,
    target_minutes: int = 3,
) -> None:
    """Generate a rule horror storyboard JSON."""
    # TODO: Wire planner, prompt builder, API client, scene generator, and writer.
    pass


def main() -> None:
    """Run the Typer application."""
    app()


if __name__ == "__main__":
    main()

