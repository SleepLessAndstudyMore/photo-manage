"""File utility functions. Implemented in S1."""
from pathlib import Path


def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)
