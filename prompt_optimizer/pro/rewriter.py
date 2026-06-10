"""Pro feature: Advanced Rewrite — completely restructures prompt for max effectiveness."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from prompt_optimizer.utils import word_count


@dataclass
class RewriteReport:
    """Advanced rewrite results."""

    original_words: int
    rewritten_words: int
    rewritten_prompt: str
    changes_summary: List[str] = field(default_factory=list)
    structure_notes: List[str] = field(default_factory=list)


# ── Section templates ───────────────────────────────────────────────

SECTION_ORDER = [
    "ROLE DEFINITION",
    "CORE RESPONSIBILITIES",
    "TOOL USAGE",
    "OUTPUT FORMAT",
    "CONSTRAINTS & BOUNDARIES",
    "TONAL GUIDANCE",
]

SECTION_HINTS: dict[str, list[str]] = {
    "ROLE DEFINITION": [
        "You are a...",
        "Your purpose is to...",
    ],
    "CORE RESPONSIBILITIES": [
        "You must:",
        "Your primary tasks:",
    ],
    "TOOL USAGE": [
        "Available tools:",
        "When to use tools:",
    ],
    "OUTPUT FORMAT": [
        "Always respond in...",
        "Format your output as...",
    ],
    "CONSTRAINTS & BOUNDARIES": [
        "Never:",
        "Do not:",
        "Limitations:",
    ],
    "TONAL GUIDANCE": [
        "Maintain a... tone",
        "Your communication style:",
    ],
}


def _extract_section(text: str, keywords: list[str]) -> str:
    """Extract lines related to a section."""
    lines = text.split("\n")
    matching: list[str] = []
    for line in lines:
        for kw in keywords:
            if kw.lower() in line.lower():
                matching.append(line)
                break
    return "\n".join(matching) if matching else ""


def _has_section_like(text: str, section_name: str) -> bool:
    """Check if the text already has something like this section."""
    markers = {
        "ROLE DEFINITION": [r"(?i)role|identity|you are|persona"],
        "CORE RESPONSIBILITIES": [r"(?i)responsibilities|tasks|must\s+do|your job|primary"],
        "TOOL USAGE": [r"(?i)tool|function call|available"],
        "OUTPUT FORMAT": [r"(?i)output format|respond|format your|json|markdown|structured"],
        "CONSTRAINTS & BOUNDARIES": [r"(?i)never|do not|constraint|boundary|limitation|restriction"],
        "TONAL GUIDANCE": [r"(?i)tone|style|voice|personality|communication"],
    }
    for marker in markers.get(section_name, []):
        if re.search(marker, text):
            return True
    return False


def advanced_rewrite(text: str) -> RewriteReport:
    """Completely restructure a prompt for maximum effectiveness."""
    original_words = word_count(text)
    report = RewriteReport(original_words=original_words, rewritten_words=0, rewritten_prompt="")

    # Detect what sections exist
    missing_sections: list[str] = []
    for section in SECTION_ORDER:
        if not _has_section_like(text, section):
            missing_sections.append(section)
            report.structure_notes.append(f"Added '{section}' section (was missing)")

    present_sections: list[str] = [
        s for s in SECTION_ORDER if _has_section_like(text, s)
    ]
    if present_sections:
        report.structure_notes.append(
            f"Existing sections recognized: {', '.join(present_sections)}"
        )

    # Build the rewritten prompt
    sections: list[str] = []

    # Title
    sections.append("# SYSTEM PROMPT (Optimized)")
    sections.append("")

    for section_name in SECTION_ORDER:
        if not _has_section_like(text, section_name) and missing_sections:
            # Generate a placeholder for missing sections
            hints = SECTION_HINTS.get(section_name, [])
            hint_text = hints[0] if hints else ""
            sections.append(f"## {section_name}")
            sections.append("")
            if hint_text:
                sections.append(f"<!-- {hint_text} — customize this section -->")
            sections.append("")
        else:
            # Try to extract relevant content
            keywords = [kw.lower() for kw in SECTION_HINTS.get(section_name, [])]
            content = _extract_section(text, keywords)
            sections.append(f"## {section_name}")
            sections.append("")
            if content:
                sections.append(content)
            sections.append("")

    rewritten = "\n".join(sections).strip()

    # Count changes
    report.changes_summary.append(f"Restructured into {len(SECTION_ORDER)} logical sections")
    if missing_sections:
        report.changes_summary.append(
            f"Added {len(missing_sections)} missing sections: {', '.join(missing_sections)}"
        )
    report.changes_summary.append(
        f"Word count: {original_words} → {word_count(rewritten)}"
    )

    report.rewritten_words = word_count(rewritten)
    report.rewritten_prompt = rewritten

    return report
