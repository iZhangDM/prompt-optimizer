"""Clarity Scorer — rates prompt clarity on specificity, actionability, and constraints."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple

from prompt_optimizer.utils import word_count


@dataclass
class ClarityReport:
    """Clarity scoring results."""

    specificity_score: int = 0  # Max 30
    specificity_notes: List[str] = field(default_factory=list)

    actionability_score: int = 0  # Max 30
    actionability_notes: List[str] = field(default_factory=list)

    constraint_clarity_score: int = 0  # Max 40
    constraint_notes: List[str] = field(default_factory=list)

    overall_score: int = 0  # Max 100
    grade: str = ""
    grade_explanation: str = ""


# ── Specificity heuristics ──────────────────────────────────────────

SPECIFICITY_POSITIVE: list[tuple[re.Pattern, str]] = [
    (re.compile(r"step\s*(?:by\s*step|\d)", re.IGNORECASE), "Contains step-by-step instructions"),
    (re.compile(r"(?:example|e\.g\.|for instance|sample)", re.IGNORECASE), "Includes concrete examples"),
    (re.compile(r"(?:specific|precise|exact|detail)"), "Uses specific/precise language"),
    (re.compile(r"(?:numbered|bullet|list)"), "Uses structured lists"),
    (re.compile(r"(?:temperature|top_p|max_tokens|max_output|parameter)", re.IGNORECASE), "References model parameters"),
]

SPECIFICITY_NEGATIVE: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(?:something|thing|stuff|whatever|etc\.|and so on)", re.IGNORECASE), "Vague placeholder words (thing, stuff, etc.)"),
    (re.compile(r"\b(?:maybe|perhaps|possibly|probably)\b", re.IGNORECASE), "Hedging language weakens specificity"),
    (re.compile(r"\b(?:good|bad|nice|great|awesome)\b", re.IGNORECASE), "Subjective adjectives instead of criteria"),
]


def score_specificity(text: str) -> Tuple[int, List[str]]:
    """Score specificity (0-30)."""
    score = 15  # Start at middle
    notes: list[str] = []

    for pat, note in SPECIFICITY_POSITIVE:
        if pat.search(text):
            score += 3
            notes.append(f"+ {note}")
    for pat, note in SPECIFICITY_NEGATIVE:
        if pat.search(text):
            score -= 3
            notes.append(f"- {note}")

    # Bonus for length/detail
    wc = word_count(text)
    if wc > 500:
        score += 3
        notes.append("+ Substantial length suggests detail")
    elif wc < 50:
        score -= 5
        notes.append("- Very short prompt likely lacks detail")

    return max(0, min(30, score)), notes


# ── Actionability heuristics ────────────────────────────────────────

ACTION_POSITIVE: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(?:you must|you should|you need to|your task is)", re.IGNORECASE), "Uses directive language (must/should/need)"),
    (re.compile(r"(?:output|respond|return|generate|produce|create|write|build)", re.IGNORECASE), "Contains action verbs"),
    (re.compile(r"(?:when|if|unless|in case)", re.IGNORECASE), "Conditional logic for different scenarios"),
    (re.compile(r"(?:first|then|next|finally|after|before)", re.IGNORECASE), "Sequential/temporal instructions"),
]

ACTION_NEGATIVE: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(?:I would like|I want|could you|would you)", re.IGNORECASE), "Polite request instead of directive (weak actionability)"),
    (re.compile(r"(?:if you want|feel free|you can if)", re.IGNORECASE), "Optional language instead of requirements"),
]


def score_actionability(text: str) -> Tuple[int, List[str]]:
    """Score actionability (0-30)."""
    score = 15
    notes: list[str] = []

    for pat, note in ACTION_POSITIVE:
        if pat.search(text):
            score += 3
            notes.append(f"+ {note}")
    for pat, note in ACTION_NEGATIVE:
        if pat.search(text):
            score -= 3
            notes.append(f"- {note}")

    return max(0, min(30, score)), notes


# ── Constraint clarity heuristics ───────────────────────────────────

CONSTRAINT_POSITIVE: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(?:never|do not|don't|cannot|must not|should not|forbidden|prohibited)", re.IGNORECASE), "Explicit prohibitions"),
    (re.compile(r"(?:only|exclusively|solely|limited to|restricted to)", re.IGNORECASE), "Scope limitations"),
    (re.compile(r"(?:boundary|boundaries|guardrail|safety|ethical)", re.IGNORECASE), "Explicit boundaries mentioned"),
    (re.compile(r"(?:tone|style|voice|persona)", re.IGNORECASE), "Tone/style constraints"),
    (re.compile(r"(?:max(?:imum)?\s*(?:length|words|characters|tokens)|min(?:imum)?\s*(?:length|words|characters|tokens))", re.IGNORECASE), "Length constraints"),
]

CONSTRAINT_NEGATIVE: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(?:helpful|harmless|honest)", re.IGNORECASE), "Relying on vague safety terms (helpful/harmless/honest is not specific)"),
]


def score_constraint_clarity(text: str) -> Tuple[int, List[str]]:
    """Score constraint clarity (0-40)."""
    score = 20
    notes: list[str] = []

    for pat, note in CONSTRAINT_POSITIVE:
        if pat.search(text):
            score += 4
            notes.append(f"+ {note}")
    for pat, note in CONSTRAINT_NEGATIVE:
        if pat.search(text):
            score -= 3
            notes.append(f"- {note}")

    return max(0, min(40, score)), notes


# ── Grade mapping ───────────────────────────────────────────────────

def grade_from_score(score: int) -> Tuple[str, str]:
    """Map numeric score to letter grade and explanation."""
    if score >= 90:
        return "A", "Excellent — production-ready prompt"
    elif score >= 80:
        return "B", "Good — minor improvements could help"
    elif score >= 70:
        return "C", "Adequate — several areas need attention"
    elif score >= 60:
        return "D", "Below average — significant gaps"
    elif score >= 40:
        return "F", "Poor — missing critical elements"
    else:
        return "F-", "Very poor — needs complete rewrite"


def score_clarity(text: str) -> ClarityReport:
    """Run full clarity scoring."""
    report = ClarityReport()

    report.specificity_score, report.specificity_notes = score_specificity(text)
    report.actionability_score, report.actionability_notes = score_actionability(text)
    report.constraint_clarity_score, report.constraint_notes = score_constraint_clarity(text)

    report.overall_score = (
        report.specificity_score + report.actionability_score + report.constraint_clarity_score
    )
    report.grade, report.grade_explanation = grade_from_score(report.overall_score)

    return report
