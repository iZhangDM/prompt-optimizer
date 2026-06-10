"""Pro feature: A/B Test Generator — creates variant prompts for comparison testing."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class ABTestReport:
    """A/B test generation results."""

    original_prompt: str
    variant_a: str = ""
    variant_a_description: str = ""
    variant_b: str = ""
    variant_b_description: str = ""
    variant_c: str = ""
    variant_c_description: str = ""
    testing_guide: List[str] = field(default_factory=list)


# ── Variant strategies ──────────────────────────────────────────────

def _variant_directive(text: str) -> str:
    """Variant A: Make it more directive/commanding."""
    # Replace polite requests with commands
    result = text
    result = re.sub(r"(?i)please\s+", "", result)
    result = re.sub(r"(?i)you could\b", "you must", result)
    result = re.sub(r"(?i)you might\b", "you should", result)
    result = re.sub(r"(?i)consider\b", "use", result)
    result = re.sub(r"(?i)try to\b", "", result)
    result = re.sub(r"(?i)if you want\b", "you are required to", result)
    result = re.sub(r"(?i)feel free to\b", "you must", result)
    # Add stronger language
    if "You are" in result:
        result = result.replace("You are", "You are required to act as")
    # Add MUST prefix
    if "IMPORTANT:" not in result and "CRITICAL:" not in result:
        result = result + "\n\nIMPORTANT: These instructions are mandatory. Do not deviate."
    return result


def _variant_minimalist(text: str) -> str:
    """Variant B: Strip to bare minimum — ultra concise."""
    lines = text.split("\n")
    # Keep only lines with strong intent
    strong_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Keep lines with action verbs, constraints, or definitions
        if re.search(
            r"(?i)(you are|you must|never|always|do not|output|format|tool|role|task|constraint|boundary)",
            stripped,
        ):
            # Strip hedging
            cleaned = re.sub(r"(?i)please\s+", "", stripped)
            cleaned = re.sub(r"(?i)\b(maybe|perhaps|possibly|probably|maybe|sort of|kind of)\b", "", cleaned)
            strong_lines.append(cleaned)
    return "\n".join(strong_lines)


def _variant_examples(text: str) -> str:
    """Variant C: Add inline examples."""
    result = text
    # If no examples exist, add them
    if not re.search(r"(?i)(?:example|e\.g\.|for instance|sample)", result):
        example_blocks = [
            "\n\n--- EXAMPLES ---",
            "Example input: 'Write a Python function to sort a list'",
            "Expected output: A Python function using sorted() with type hints and docstring",
            "",
            "Example input: 'Explain quantum computing'",
            "Expected output: 3-paragraph explanation starting with analogy, then technical detail, then applications",
        ]
        result = result.rstrip() + "\n" + "\n".join(example_blocks)
    return result


def generate_ab_variants(text: str) -> ABTestReport:
    """Generate three variant prompts for A/B testing."""
    report = ABTestReport(original_prompt=text)

    report.variant_a = _variant_directive(text)
    report.variant_a_description = "DIRECTIVE: Stronger command language, removed politeness, added mandatory compliance marker"

    report.variant_b = _variant_minimalist(text)
    report.variant_b_description = "MINIMALIST: Stripped to essential instructions only, removed all hedging and filler"

    report.variant_c = _variant_examples(text)
    report.variant_c_description = "EXAMPLES: Added concrete input/output examples to ground the model's behavior"

    report.testing_guide = [
        "1. Run each variant with the SAME set of 10-20 test inputs",
        "2. Rate outputs on: accuracy, format compliance, helpfulness, safety",
        "3. Use blind evaluation — don't know which variant produced which output",
        "4. Track: response time, token usage, error rate for each variant",
        "5. Statistical significance: at least 30 tests before concluding",
        "6. Winner = highest average score across all metrics",
    ]

    return report
