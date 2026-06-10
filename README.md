# Agent Prompt Optimizer (APO)

**Optimize AI agent system prompts for clarity, safety, and effectiveness.**

A zero-dependency, pure-Python CLI tool that analyzes system prompts and produces actionable optimization reports. Free core features with paid Pro upgrades ($9 one-time).

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/deps-zero-brightgreen)]()
[![Type Hints](https://img.shields.io/badge/type%20hints-full-brightgreen)]()

---

## Quick Start

```bash
# Install
pip install agent-prompt-optimizer

# Optimize a prompt
apo optimize prompt.txt

# Or from the repo directly
python apo.py optimize samples/bad_prompt.txt
```

## Features

### Free Tier (open source)

| Feature | Description |
|---------|-------------|
| **Structure Analyzer** | Checks for: role definition, output format, tool usage, constraints/boundaries |
| **Length Optimizer** | Removes 80+ redundancy patterns, tightens language without losing meaning |
| **Clarity Scorer** | Rates specificity, actionability, and constraint clarity on a 0–100 scale |
| **Anti-Injection Hardening** | Detects 12 injection vulnerability patterns + applies hardening rules |

### Pro Tier ($9 one-time)

| Feature | Description |
|---------|-------------|
| **Advanced Rewrite** | Completely restructures prompts into logical sections |
| **A/B Test Generator** | Creates 3 variant prompts with different strategies + testing guide |
| **Model-Specific Optimization** | Tailors prompts for GPT-4, Claude, DeepSeek, Gemini, Llama, Mistral |

## Usage

### Basic optimization

```bash
# From a file
apo optimize prompt.txt

# Inline text
apo optimize --text "You are a helpful assistant..."

# From stdin
cat prompt.txt | apo optimize -

# Save output
apo optimize prompt.txt -o optimized.txt

# JSON output (machine-readable)
apo optimize prompt.txt --json

# Single module
apo optimize prompt.txt --only structure
```

### Pro features (license required)

```bash
# Advanced restructure
apo pro rewrite prompt.txt -o rewritten.txt

# Generate A/B test variants
apo pro ab-test prompt.txt -o variants.txt

# Model-specific optimization
apo pro model gpt-4 prompt.txt -o gpt4-prompt.txt
apo pro model claude prompt.txt
apo pro model deepseek prompt.txt

# List supported models
apo pro model --list-models
```

### License management

```bash
# Check license status
apo license check

# Install license
apo license install <your-license-key>

# Generate keys (for sellers)
apo license generate user@email.com --expiry 2026-12-31
```

## Sample Output

Running `apo optimize samples/bad_prompt.txt`:

```
============================================================
AGENT PROMPT OPTIMIZER — Analysis Report
============================================================
Prompt length: 200 words, 1121 chars

1. PROMPT STRUCTURE ANALYSIS
  Overall: 12/40

  ✓ Role Definition         (6/10)
    You are a helpful AI assistant. Please help the user with whatever...
  ✗ Output Format           (0/10)
  ✗ Tool Usage              (0/10)
  ✓ Constraints             (6/10)
    Don't do anything bad I guess. It's important to note that you should...

  Suggestions:
    • Add a clear output format specification section...
    • Add a clear tool usage instruction section...

2. LENGTH OPTIMIZATION
  Original:   200 words
  Optimized:  157 words
  Removed:    -43 words (21.5%)

3. CLARITY SCORE
  Overall: 46/100  Grade: F
  Below average — significant gaps
  Specificity:      12/30
  Actionability:    14/30
  Constraint Clarity: 20/40

4. ANTI-INJECTION HARDENING
  Risk Level: LOW  (0/100)
  No common injection patterns detected.
```

## Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | Structure analysis, length optimization, clarity scoring, anti-injection hardening |
| **Pro** | **$9** (one-time) | Advanced rewrite, A/B test generator, model-specific optimization, priority support |

[Get a Pro license →](https://promptoptimizer.dev/pro)

## Installation

### Via pip

```bash
pip install agent-prompt-optimizer
```

### From source

```bash
git clone https://github.com/promptoptimizer/apo.git
cd apo
pip install -e .
```

### No install (run directly)

```bash
git clone https://github.com/promptoptimizer/apo.git
cd apo
python apo.py optimize samples/bad_prompt.txt
```

**Requirements:** Python 3.9+. Zero external dependencies. Works on Linux, macOS, and Windows (WSL).

## Architecture

```
prompt-optimizer/
├── apo.py                          # CLI entry point
├── pyproject.toml                  # Package metadata
├── README.md
├── samples/
│   └── bad_prompt.txt              # Demo: a deliberately weak prompt
├── prompt_optimizer/
│   ├── __init__.py
│   ├── cli.py                      # Argument parsing + output formatting
│   ├── utils.py                    # Shared helpers
│   ├── analyzer.py                 # Structure analyzer
│   ├── optimizer.py                # Length optimizer (80+ redundancy patterns)
│   ├── scorer.py                   # Clarity scorer (3 dimensions)
│   ├── anti_injection.py           # Anti-injection detection + hardening
│   └── pro/
│       ├── __init__.py
│       ├── license.py              # HMAC-based license key system
│       ├── rewriter.py             # Advanced prompt restructure
│       ├── ab_generator.py         # A/B variant generator
│       └── model_optimizer.py      # Model-specific profiles (7 models)
└── tests/
    └── test_basic.py
```

## How It Works

### Structure Analyzer
Uses regex heuristics to detect four critical prompt components: role definition, output format specification, tool usage instructions, and constraints/boundaries. Each dimension scored 0–10.

### Length Optimizer
Applies 80+ redundancy reduction patterns covering: wordy phrases, hedging language, filler words, redundant pairs, and polite padding. Reductions of 15–30% are common.

### Clarity Scorer
Evaluates prompts on three axes:
- **Specificity** (0–30): Concrete examples, precise language, step-by-step instructions
- **Actionability** (0–30): Directive verbs, conditional logic, sequential instructions
- **Constraint Clarity** (0–40): Explicit prohibitions, scope limits, tone/style boundaries

### Anti-Injection Hardening
Detects 12 vulnerability classes: override commands, system role redefinition, authority spoofing, prompt extraction, encoding evasion, jailbreak patterns, and more. Applies three hardening rules to the output.

### Model-Specific Optimization
Seven model profiles with native formatting and behavioral optimizations:
- **GPT-4**: Structured markdown, example emphasis
- **Claude**: XML delimiters, harmlessness framing
- **DeepSeek**: Reasoning cues, bilingual support
- **Gemini**: Numbered tasks, safety disclaimers
- **Llama**: Native `<|start_header_id|>` format
- **Mistral**: Concise formatting, tool emphasis
- **GPT-3.5**: Constraint repetition, simplified language

## License

MIT License. See [LICENSE](LICENSE) for details.

The Pro features require a paid license key ($9 one-time). The license system uses HMAC-SHA256 signed keys — keys are simple text strings that can be emailed to customers.

---

**Made with ❤️ for prompt engineers.**
