"""Compatibility CLI wrapper for AI Writer Room."""

from __future__ import annotations

from pathlib import Path
import sys


PACKAGE_PARENT = Path(__file__).resolve().parent.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from ai_writer_room.generate_storyboard import main


if __name__ == "__main__":
    main()
