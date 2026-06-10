"""CLI argument parsing and dispatch for Agent Prompt Optimizer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from prompt_optimizer import __version__
from prompt_optimizer.utils import (
    bold,
    green,
    red,
    yellow,
    dim,
    header,
    read_input,
    word_count,
    char_count,
)
from prompt_optimizer.analyzer import analyze_structure
from prompt_optimizer.optimizer import optimize_length
from prompt_optimizer.scorer import score_clarity
from prompt_optimizer.anti_injection import analyze_injection_risk


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="apo",
        description="Agent Prompt Optimizer — analyze and optimize AI agent system prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  apo optimize prompt.txt              # Optimize a prompt file
  apo optimize --text "You are a..."   # Optimize inline prompt text
  cat prompt.txt | apo optimize -      # Optimize from stdin
  apo pro rewrite prompt.txt           # Pro: advanced rewrite
  apo pro ab-test prompt.txt           # Pro: generate A/B test variants
  apo pro model gpt-4 prompt.txt       # Pro: optimize for specific model
  apo license --generate user@email.com --expiry 2026-12-31 --secret mykey
  apo license --check                  # Check current license status
        """,
    )
    parser.add_argument(
        "--version", action="version", version=f"apo v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # ── optimize (free core features) ───────────────────────────────
    opt = subparsers.add_parser("optimize", help="Run full optimization (free features)")
    opt.add_argument(
        "input",
        nargs="?",
        help="Prompt file path (use '-' for stdin, or --text for inline)",
    )
    opt.add_argument(
        "--text", "-t", help="Inline prompt text (instead of file)"
    )
    opt.add_argument(
        "--output", "-o", help="Save optimized prompt to file"
    )
    opt.add_argument(
        "--json", action="store_true", help="Output as JSON (for piping)"
    )
    opt.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )
    opt.add_argument(
        "--only", choices=["structure", "length", "clarity", "injection"],
        help="Run only one analysis module"
    )

    # ── pro (paid features) ─────────────────────────────────────────
    pro = subparsers.add_parser("pro", help="Pro features (license required)")
    pro_sub = pro.add_subparsers(dest="pro_command")

    # pro rewrite
    rewrite = pro_sub.add_parser("rewrite", help="Advanced prompt restructure")
    rewrite.add_argument("input", help="Prompt file path")
    rewrite.add_argument("--output", "-o", help="Save output to file")

    # pro ab-test
    ab = pro_sub.add_parser("ab-test", help="Generate A/B test variants")
    ab.add_argument("input", help="Prompt file path")
    ab.add_argument("--output", "-o", help="Save output to file")

    # pro model
    model = pro_sub.add_parser("model", help="Model-specific optimization")
    model.add_argument("model_name", help="Target model (gpt-4, claude, deepseek, gemini, llama, mistral)")
    model.add_argument("input", help="Prompt file path")
    model.add_argument("--output", "-o", help="Save output to file")
    model.add_argument("--list-models", action="store_true", help="List supported models")

    # ── license management ──────────────────────────────────────────
    lic = subparsers.add_parser("license", help="License key management")
    lic_sub = lic.add_subparsers(dest="license_command")

    lic_check = lic_sub.add_parser("check", help="Check license status")

    lic_gen = lic_sub.add_parser("generate", help="Generate a license key (for sellers)")
    lic_gen.add_argument("email", help="Customer email")
    lic_gen.add_argument("--expiry", required=True, help="Expiry date (YYYY-MM-DD)")
    lic_gen.add_argument("--secret", default="apo-pro-secret-2024", help="Signing secret")

    lic_install = lic_sub.add_parser("install", help="Install a license key")
    lic_install.add_argument("key", help="License key string")

    return parser


def run_optimize(args: argparse.Namespace) -> None:
    """Run the free optimization pipeline."""
    prompt = read_input(args.input, args.text)

    if not prompt.strip():
        print(red("Error: No prompt provided. Use --text, a file path, or pipe via stdin."))
        sys.exit(1)

    use_json: bool = args.json
    only: Optional[str] = args.only

    if not use_json:
        print(header("AGENT PROMPT OPTIMIZER — Analysis Report"))
        print(f"{dim('Prompt length:')} {word_count(prompt)} words, {char_count(prompt)} chars")
        print()

    # ── 1. Structure Analysis ───────────────────────────────────────
    if not only or only == "structure":
        report = analyze_structure(prompt)
        if use_json:
            import json
            print(json.dumps({
                "structure": {
                    "role_definition": {"found": report.has_role_definition, "score": report.role_score, "excerpt": report.role_excerpt},
                    "output_format": {"found": report.has_output_format, "score": report.output_score, "excerpt": report.output_format_excerpt},
                    "tool_usage": {"found": report.has_tool_usage, "score": report.tool_score, "excerpt": report.tool_excerpt},
                    "constraints": {"found": report.has_constraints, "score": report.constraint_score, "excerpt": report.constraint_excerpt},
                    "overall_score": report.overall_score,
                    "max_score": report.max_score,
                    "suggestions": report.suggestions,
                }
            }, indent=2))
        else:
            _print_structure_report(report, args.no_color)

    # ── 2. Length Optimization ──────────────────────────────────────
    if not only or only == "length":
        len_report = optimize_length(prompt)
        if use_json:
            import json
            print(json.dumps({
                "length": {
                    "original_words": len_report.original_words,
                    "optimized_words": len_report.optimized_words,
                    "words_removed": len_report.words_removed,
                    "reduction_pct": len_report.reduction_pct,
                    "changes_count": len(len_report.changes),
                    "optimized_text": len_report.optimized_text,
                }
            }, indent=2))
        else:
            _print_length_report(len_report, args.no_color)

    # ── 3. Clarity Scoring ──────────────────────────────────────────
    if not only or only == "clarity":
        clarity = score_clarity(prompt)
        if use_json:
            import json
            print(json.dumps({
                "clarity": {
                    "specificity": {"score": clarity.specificity_score, "notes": clarity.specificity_notes},
                    "actionability": {"score": clarity.actionability_score, "notes": clarity.actionability_notes},
                    "constraint_clarity": {"score": clarity.constraint_clarity_score, "notes": clarity.constraint_notes},
                    "overall_score": clarity.overall_score,
                    "max_score": 100,
                    "grade": clarity.grade,
                    "explanation": clarity.grade_explanation,
                }
            }, indent=2))
        else:
            _print_clarity_report(clarity, args.no_color)

    # ── 4. Anti-Injection Analysis ──────────────────────────────────
    if not only or only == "injection":
        injection = analyze_injection_risk(prompt)
        if use_json:
            import json
            print(json.dumps({
                "anti_injection": {
                    "risk_level": injection.risk_level,
                    "risk_score": injection.risk_score,
                    "vulnerabilities": injection.vulnerabilities,
                    "hardening_suggestions": injection.hardening_suggestions,
                    "hardened_prompt": injection.hardened_prompt,
                }
            }, indent=2))
        else:
            _print_injection_report(injection, args.no_color)

    # ── Output the optimized prompt ─────────────────────────────────
    if not only or only == "length":
        optimized = optimize_length(prompt).optimized_text
    else:
        optimized = prompt

    if args.output:
        Path(args.output).write_text(optimized, encoding="utf-8")
        if not use_json:
            print(green(f"\n✓ Optimized prompt saved to: {args.output}"))
    elif not use_json and not only:
        print(header("OPTIMIZED PROMPT"))
        print(optimized)


def run_pro(args: argparse.Namespace) -> None:
    """Run Pro features (license check + dispatch)."""
    from prompt_optimizer.pro.license import check_pro_access

    # List models
    if hasattr(args, "list_models") and args.list_models:
        from prompt_optimizer.pro.model_optimizer import MODEL_PROFILES
        print(bold("Supported models:"))
        for key, profile in MODEL_PROFILES.items():
            print(f"  {green(key):20s} {profile['display']}")
        return

    license_info = check_pro_access()
    if not license_info.valid:
        print(red(f"Pro feature requires a valid license."))
        print(f"  {license_info.error}")
        print(f"  Get one at: https://promptoptimizer.dev/pro")
        print(f"  Run: apo license install <your-key>")
        sys.exit(1)

    print(dim(f"✓ License valid — {license_info.email} ({license_info.days_remaining} days remaining)"))

    if args.pro_command == "rewrite":
        from prompt_optimizer.pro.rewriter import advanced_rewrite
        prompt = Path(args.input).read_text(encoding="utf-8")
        result = advanced_rewrite(prompt)

        print(header("ADVANCED REWRITE"))
        for note in result.structure_notes:
            print(f"  {yellow('•')} {note}")
        for change in result.changes_summary:
            print(f"  {green('✓')} {change}")
        print(header("REWRITTEN PROMPT"))
        print(result.rewritten_prompt)

        if args.output:
            Path(args.output).write_text(result.rewritten_prompt, encoding="utf-8")
            print(green(f"\n✓ Saved to: {args.output}"))

    elif args.pro_command == "ab-test":
        from prompt_optimizer.pro.ab_generator import generate_ab_variants
        prompt = Path(args.input).read_text(encoding="utf-8")
        result = generate_ab_variants(prompt)

        print(header("A/B TEST VARIANTS"))
        print()
        print(bold("Variant A — ") + result.variant_a_description)
        print("-" * 60)
        print(result.variant_a)
        print()
        print(bold("Variant B — ") + result.variant_b_description)
        print("-" * 60)
        print(result.variant_b)
        print()
        print(bold("Variant C — ") + result.variant_c_description)
        print("-" * 60)
        print(result.variant_c)
        print()
        print(header("TESTING GUIDE"))
        for step in result.testing_guide:
            print(f"  {step}")

        if args.output:
            out = (
                "=== VARIANT A (Directive) ===\n" + result.variant_a + "\n\n"
                "=== VARIANT B (Minimalist) ===\n" + result.variant_b + "\n\n"
                "=== VARIANT C (Examples) ===\n" + result.variant_c + "\n"
            )
            Path(args.output).write_text(out, encoding="utf-8")
            print(green(f"\n✓ Saved to: {args.output}"))

    elif args.pro_command == "model":
        from prompt_optimizer.pro.model_optimizer import optimize_for_model, SUPPORTED_MODELS
        prompt = Path(args.input).read_text(encoding="utf-8")
        model_name = args.model_name
        result = optimize_for_model(prompt, model_name)

        if not result.changes or result.changes[0].startswith("Unknown"):
            print(red(f"Unknown model: {model_name}"))
            print(f"Supported: {', '.join(SUPPORTED_MODELS)}")
            sys.exit(1)

        print(header(f"MODEL OPTIMIZATION — {result.model}"))
        print(f"  {dim(result.model_notes)}")
        print()
        print(bold("Changes applied:"))
        for change in result.changes:
            print(f"  {green('✓')} {change}")
        print(header("OPTIMIZED PROMPT"))
        print(result.optimized_prompt)

        if args.output:
            Path(args.output).write_text(result.optimized_prompt, encoding="utf-8")
            print(green(f"\n✓ Saved to: {args.output}"))

    else:
        print("Usage: apo pro {rewrite|ab-test|model} ...")
        print("Run 'apo pro --help' for details.")


def run_license(args: argparse.Namespace) -> None:
    """Handle license commands."""
    if args.license_command == "check":
        from prompt_optimizer.pro.license import check_pro_access, find_license
        key_path = find_license()
        info = check_pro_access()

        print(header("LICENSE STATUS"))
        print(f"  License file: {key_path or 'Not found'}")

        if info.valid:
            print(f"  Status:       {green('VALID')}")
            print(f"  Email:        {info.email}")
            print(f"  Expires:      {info.expiry_date}")
            print(f"  Days left:    {green(str(info.days_remaining))}")
        else:
            print(f"  Status:       {red('INVALID')}")
            print(f"  Reason:       {info.error}")

    elif args.license_command == "generate":
        from prompt_optimizer.pro.license import generate_license
        key = generate_license(args.email, args.expiry)
        print(header("GENERATED LICENSE KEY"))
        print(f"  {bold(key)}")
        print()
        print(dim("Give this key to the customer. They install it with:"))
        print(dim(f"  apo license install {key}"))

    elif args.license_command == "install":
        from prompt_optimizer.pro.license import save_license, parse_license
        info = parse_license(args.key)
        if info.valid:
            path = save_license(args.key)
            print(green(f"✓ License installed to {path}"))
            print(f"  Email:    {info.email}")
            print(f"  Expires:  {info.expiry_date}")
            print(f"  Days:     {info.days_remaining}")
        else:
            print(red(f"Invalid license: {info.error}"))
            sys.exit(1)

    else:
        print("Usage: apo license {check|generate|install}")
        print("Run 'apo license --help' for details.")


# ── Pretty-print helpers ────────────────────────────────────────────

def _print_structure_report(report, no_color: bool) -> None:
    """Pretty-print structure analysis."""
    def c(s: str, code: str) -> str:
        if no_color:
            return s
        return code + s + "\033[0m"

    print(bold("1. PROMPT STRUCTURE ANALYSIS"))
    print(f"  Overall: {report.overall_score}/{report.max_score}")
    print()

    dims = [
        ("Role Definition", report.has_role_definition, report.role_score, report.role_excerpt),
        ("Output Format", report.has_output_format, report.output_score, report.output_format_excerpt),
        ("Tool Usage", report.has_tool_usage, report.tool_score, report.tool_excerpt),
        ("Constraints", report.has_constraints, report.constraint_score, report.constraint_excerpt),
    ]

    for name, found, score, excerpt in dims:
        status = c("✓", "\033[32m") if found else c("✗", "\033[31m")
        print(f"  {status} {name:<20s} ({score}/10)", end="")
        if excerpt and found:
            print(f"\n    {c(excerpt[:100], '\033[2m')}")
        else:
            print()

    if report.suggestions:
        print(f"\n  {c('Suggestions:', '\033[33m')}")
        for sug in report.suggestions[:5]:
            print(f"    • {sug}")


def _print_length_report(report, no_color: bool) -> None:
    """Pretty-print length optimization results."""
    def c(s: str, code: str) -> str:
        if no_color:
            return s
        return code + s + "\033[0m"

    print(bold("\n2. LENGTH OPTIMIZATION"))
    print(f"  Original:   {report.original_words} words")
    print(f"  Optimized:  {report.optimized_words} words")
    removal = c(f"-{report.words_removed} words ({report.reduction_pct}%)", "\033[32m")
    print(f"  Removed:    {removal}")
    if report.changes:
        print(f"\n  {c('Changes:', '\033[2m')}")
        for ch in report.changes[:10]:
            print(f"    • '{ch['pattern']}' → '{ch['replacement']}' ({ch['matches']}×)")


def _print_clarity_report(report, no_color: bool) -> None:
    """Pretty-print clarity scoring."""
    def c(s: str, code: str) -> str:
        if no_color:
            return s
        return code + s + "\033[0m"

    print(bold("\n3. CLARITY SCORE"))
    grade_color = "\033[32m" if report.overall_score >= 80 else "\033[33m" if report.overall_score >= 60 else "\033[31m"
    print(f"  Overall: {c(f'{report.overall_score}/100', grade_color)}  Grade: {c(report.grade, grade_color)}")
    print(f"  {c(report.grade_explanation, '\033[2m')}")
    print()
    print(f"  Specificity:      {report.specificity_score}/30")
    for n in report.specificity_notes[:3]:
        print(f"    {n}")
    print(f"  Actionability:    {report.actionability_score}/30")
    for n in report.actionability_notes[:3]:
        print(f"    {n}")
    print(f"  Constraint Clarity: {report.constraint_clarity_score}/40")
    for n in report.constraint_notes[:3]:
        print(f"    {n}")


def _print_injection_report(report, no_color: bool) -> None:
    """Pretty-print anti-injection analysis."""
    def c(s: str, code: str) -> str:
        if no_color:
            return s
        return code + s + "\033[0m"

    level_color = {
        "LOW": "\033[32m",
        "MEDIUM": "\033[33m",
        "HIGH": "\033[31m",
        "CRITICAL": "\033[1;31m",
    }.get(report.risk_level, "\033[0m")

    print(bold("\n4. ANTI-INJECTION HARDENING"))
    print(f"  Risk Level: {c(report.risk_level, level_color)}  ({report.risk_score}/100)")

    if report.vulnerabilities:
        print(f"\n  {c('Vulnerabilities detected:', '\033[31m')}")
        for v in report.vulnerabilities:
            print(f"    • {v['name']} (severity: {v['severity']})")
            print(f"      {v['explanation']}")
    else:
        print(f"\n  {c('No common injection patterns detected.', '\033[32m')}")

    if report.hardening_suggestions:
        print(f"\n  {c('Hardening suggestions:', '\033[33m')}")
        for sug in report.hardening_suggestions:
            print(f"    • {sug}")
