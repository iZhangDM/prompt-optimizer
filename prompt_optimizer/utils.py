"""Shared utilities for the prompt optimizer."""

from __future__ import annotations

import re
import sys
from typing import Optional


def read_input(path: Optional[str] = None, text: Optional[str] = None) -> str:
    """Read prompt text from file, --text flag, or stdin."""
    if text:
        return text
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def word_count(s: str) -> int:
    """Count words in a string."""
    return len(s.split())


def char_count(s: str) -> int:
    """Count non-whitespace characters."""
    return len(re.sub(r"\s+", "", s))


def bold(s: str) -> str:
    """Terminal bold text."""
    return f"\033[1m{s}\033[0m"


def green(s: str) -> str:
    """Terminal green text."""
    return f"\033[32m{s}\033[0m"


def red(s: str) -> str:
    """Terminal red text."""
    return f"\033[31m{s}\033[0m"


def yellow(s: str) -> str:
    """Terminal yellow text."""
    return f"\033[33m{s}\033[0m"


def dim(s: str) -> str:
    """Terminal dim text."""
    return f"\033[2m{s}\033[0m"


def header(s: str) -> str:
    """Print a section header."""
    width = 60
    return f"\n{bold('=' * width)}\n{bold(s)}\n{bold('=' * width)}"
