"""Prompt Structure Analyzer — checks prompt structure quality."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from prompt_optimizer.utils import word_count


@dataclass
class StructureReport:
    """Structured analysis of a prompt's components."""

    # Four dimensions
    has_role_definition: bool = False
    role_excerpt: str = ""
    role_score: int = 0

    has_output_format: bool = False
    output_format_excerpt: str = ""
    output_score: int = 0

    has_tool_usage: bool = False
    tool_excerpt: str = ""
    tool_score: int = 0

    has_constraints: bool = False
    constraint_excerpt: str = ""
    constraint_score: int = 0

    # Summary
    overall_score: int = 0
    max_score: int = 40
    suggestions: List[str] = field(default_factory=list)
    total_words: int = 0


# ── Detection heuristics ─────────────────────────────────────────────

ROLE_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?:^|\n)\s*(?:You are|You're|Act as|You work as|Your role is|You are an?|You serve as)", re.IGNORECASE),
    re.compile(r"(?:role|persona|identity)[\s:]*[:=-]", re.IGNORECASE),
]

OUTPUT_FORMAT_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?:output format|format your (?:answer|response|output)|respond (?:in|with|using))", re.IGNORECASE),
    re.compile(r"(?:JSON|XML|markdown|YAML|CSV|table|code block)", re.IGNORECASE),
    re.compile(r"(?:always|must|should|format).+(?:structured|formatted)", re.IGNORECASE),
]

TOOL_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?:tool|function)\s*(?:call|calling|use|usage|invoke|invocation)", re.IGNORECASE),
    re.compile(r"(?:use the|call the|invoke the|available (?:tools|functions))", re.IGNORECASE),
    re.compile(r"(?:<tool>|tool_choice|function_call)", re.IGNORECASE),
]

CONSTRAINT_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?:do not|don't|never|must not|cannot|should not|forbidden|prohibited|restricted|banned)", re.IGNORECASE),
    re.compile(r"(?:constraint|boundary|limitation|restriction|rule|policy|guardrail)", re.IGNORECASE),
    re.compile(r"(?:only|exclusively|solely|limited to|restricted to)", re.IGNORECASE),
]


def extract_excerpt(text: str, patterns: list[re.Pattern]) -> str:
    """Return the first matching line/sentence as an excerpt."""
    for pat in patterns:
        m = pat.search(text)
        if m:
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 80)
            snippet = text[start:end].strip()
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            return snippet
    return ""


def assess_dimension(
    text: str, patterns: list[re.Pattern], dimension_name: str
) -> tuple[bool, str, int, list[str]]:
    """Assess a single dimension and return (found, excerpt, score, suggestions)."""
    found = False
    excerpt = extract_excerpt(text, patterns)
    suggestions: list[str] = []

    if excerpt:
        found = True
    else:
        suggestions.append(
            f"Add a clear {dimension_name} section. Example: 'You are a senior Python developer...'"
        )

    # Score: 0 if missing, 8–10 if present and explicit
    if found:
        # Check specificity: longer excerpt with multiple matches = stronger
        matches = sum(1 for p in patterns if p.search(text))
        if matches >= 3:
            score = 10
        elif matches == 2:
            score = 8
        else:
            score = 6
    else:
        score = 0

    return found, excerpt, score, suggestions


def analyze_structure(text: str) -> StructureReport:
    """Analyze a prompt's structure and return a report."""
    report = StructureReport()
    report.total_words = word_count(text)

    # Role
    report.has_role_definition, report.role_excerpt, report.role_score, role_sugs = assess_dimension(
        text, ROLE_PATTERNS, "role definition"
    )
    report.suggestions.extend(role_sugs)

    # Output format
    report.has_output_format, report.output_format_excerpt, report.output_score, out_sugs = assess_dimension(
        text, OUTPUT_FORMAT_PATTERNS, "output format specification"
    )
    report.suggestions.extend(out_sugs)

    # Tool usage
    report.has_tool_usage, report.tool_excerpt, report.tool_score, tool_sugs = assess_dimension(
        text, TOOL_PATTERNS, "tool usage instruction"
    )
    report.suggestions.extend(tool_sugs)

    # Constraints
    report.has_constraints, report.constraint_excerpt, report.constraint_score, con_sugs = assess_dimension(
        text, CONSTRAINT_PATTERNS, "constraints/boundaries"
    )
    report.suggestions.extend(con_sugs)

    report.overall_score = (
        report.role_score + report.output_score + report.tool_score + report.constraint_score
    )

    return report
