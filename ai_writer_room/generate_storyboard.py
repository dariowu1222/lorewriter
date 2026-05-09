"""Programmatic entry point for storyboard generation."""

from __future__ import annotations

from pathlib import Path


def generate_storyboard(
    premise: str,
    output_path: Path | None = None,
    target_minutes: int = 3,
) -> None:
    """Generate a 3-minute rule horror storyboard JSON."""
    # TODO: Coordinate story planning, prompt building, generation, and output.
    pass


def main() -> None:
    """Run storyboard generation from a script entry point."""
    # TODO: Delegate CLI parsing to ai_writer_room.cli or a thin Typer command.
    pass


if __name__ == "__main__":
    main()

