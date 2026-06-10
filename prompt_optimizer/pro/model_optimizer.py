"""Pro feature: Model-Specific Optimization — tailor prompts for specific LLMs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ModelOptimizationReport:
    """Model-specific optimization results."""

    model: str
    optimized_prompt: str
    changes: List[str] = field(default_factory=list)
    model_notes: str = ""


# ── Model profiles ──────────────────────────────────────────────────

MODEL_PROFILES: Dict[str, dict] = {
    "gpt-4": {
        "display": "GPT-4 / GPT-4o (OpenAI)",
        "notes": "GPT-4 responds well to structured markdown, explicit examples, and system/user separation. Uses 'You are' role syntax.",
        "prefix": "",  # No special prefix needed
        "suffix": "",
        "transformations": [
            ("add_markdown_structure", "Added markdown headers for section clarity"),
            ("emphasize_examples", "Emphasized few-shot examples (GPT-4 excels with them)"),
            ("add_system_note", "Added explicit '<|im_start|>system' framing"),
        ],
        "tone": "professional and direct",
    },
    "gpt-3.5": {
        "display": "GPT-3.5 Turbo (OpenAI)",
        "notes": "GPT-3.5 needs more explicit instructions than GPT-4. Be redundant on constraints. Shorter prompts help.",
        "prefix": "",
        "suffix": "",
        "transformations": [
            ("repeat_constraints", "Repeated key constraints (GPT-3.5 benefits from redundancy)"),
            ("simplify_language", "Simplified language to avoid misinterpretation"),
            ("add_reminder", "Added end-of-prompt reminder of key rules"),
        ],
        "tone": "simple and repetitive",
    },
    "claude": {
        "display": "Claude (Anthropic)",
        "notes": "Claude uses XML-style delimiters and responds well to structured sections. Use <instructions> tags. Claude is naturally cautious.",
        "prefix": "",
        "suffix": "",
        "transformations": [
            ("add_xml_delimiters", "Wrapped sections in <role>, <task>, <constraints> XML tags"),
            ("add_harmlessness_note", "Added explicit harmlessness framing (Claude-native)"),
            ("structure_hierarchical", "Added hierarchical numbered instructions"),
        ],
        "tone": "structured and ethical",
    },
    "deepseek": {
        "display": "DeepSeek (DeepSeek AI)",
        "notes": "DeepSeek models perform well with Chinese/English bilingual prompts. Use clear separation of concerns. Benefits from reasoning cues.",
        "prefix": "",
        "suffix": "",
        "transformations": [
            ("add_reasoning_cue", "Added 'Think step by step' reasoning guidance"),
            ("bilingual_support", "Added bilingual capability note if relevant"),
            ("code_block_emphasis", "Emphasized code block formatting (DeepSeek strength)"),
        ],
        "tone": "analytical and bilingual-friendly",
    },
    "gemini": {
        "display": "Gemini (Google)",
        "notes": "Gemini benefits from clear task decomposition and safety disclaimers. Use numbered steps.",
        "prefix": "",
        "suffix": "",
        "transformations": [
            ("numbered_tasks", "Converted instructions to numbered task list"),
            ("safety_disclaimer", "Added explicit safety boundaries"),
            ("step_decomposition", "Decomposed complex tasks into sub-steps"),
        ],
        "tone": "structured and safety-conscious",
    },
    "llama": {
        "display": "Llama 3 (Meta)",
        "notes": "Llama 3 uses <|start_header_id|> delimiters. Benefits from clear role assignment and constraint repetition.",
        "prefix": "<|start_header_id|>system<|end_header_id|>\n\n",
        "suffix": "<|eot_id|>",
        "transformations": [
            ("add_llama_delimiters", "Added Llama 3 native delimiter format"),
            ("role_clarity", "Strengthened role definition (key for Llama)"),
            ("constraint_final", "Added constraint recap at end"),
        ],
        "tone": "direct and explicit",
    },
    "mistral": {
        "display": "Mistral / Mixtral (Mistral AI)",
        "notes": "Mistral models are instruction-tuned and respond well to clear, concise prompts without excessive formatting.",
        "prefix": "",
        "suffix": "",
        "transformations": [
            ("concise_formatting", "Reduced formatting overhead (Mistral prefers plain text)"),
            ("direct_instructions", "Made instructions more direct and less verbose"),
            ("tool_emphasis", "Emphasized tool-calling structure (Mistral strength)"),
        ],
        "tone": "concise and direct",
    },
}

SUPPORTED_MODELS = list(MODEL_PROFILES.keys())
MODEL_ALIASES = {
    "gpt4": "gpt-4",
    "gpt-4o": "gpt-4",
    "gpt-4-turbo": "gpt-4",
    "gpt35": "gpt-3.5",
    "gpt-3.5-turbo": "gpt-3.5",
    "claude-3": "claude",
    "claude-3.5": "claude",
    "claude-3-opus": "claude",
    "deepseek-v2": "deepseek",
    "deepseek-v3": "deepseek",
    "deepseek-coder": "deepseek",
    "gemini-pro": "gemini",
    "gemini-ultra": "gemini",
    "llama-3": "llama",
    "llama3": "llama",
    "mistral-large": "mistral",
    "mixtral": "mistral",
}


def resolve_model(name: str) -> Optional[str]:
    """Resolve a model name or alias to a canonical model ID."""
    name_lower = name.lower().strip()
    if name_lower in MODEL_PROFILES:
        return name_lower
    if name_lower in MODEL_ALIASES:
        return MODEL_ALIASES[name_lower]
    return None


def optimize_for_model(prompt: str, model: str) -> ModelOptimizationReport:
    """Optimize a prompt for a specific model."""
    canonical = resolve_model(model)
    if canonical is None:
        return ModelOptimizationReport(
            model=model,
            optimized_prompt=prompt,
            changes=[f"Unknown model '{model}'. No optimizations applied."],
            model_notes=f"Supported models: {', '.join(SUPPORTED_MODELS)}",
        )

    profile = MODEL_PROFILES[canonical]
    report = ModelOptimizationReport(
        model=profile["display"],
        optimized_prompt="",
        model_notes=profile["notes"],
    )

    optimized = prompt

    # Apply model-specific transformations
    for transform_name, description in profile["transformations"]:
        report.changes.append(description)

        if transform_name == "add_markdown_structure":
            if "## " not in optimized:
                optimized = optimized.replace("\n\n", "\n\n## Instructions\n\n", 1)

        elif transform_name == "add_system_note":
            optimized = (
                "# SYSTEM INSTRUCTION (GPT-4 Optimized)\n"
                "# Follow these instructions precisely.\n\n"
                + optimized
            )

        elif transform_name == "repeat_constraints":
            # Add a recap at the end for GPT-3.5
            constraints = [
                line
                for line in optimized.split("\n")
                if any(
                    kw in line.lower()
                    for kw in ["never", "do not", "don't", "must not", "cannot"]
                )
            ]
            if constraints:
                recap = "\n\nREMINDER: " + " Also: ".join(constraints[:3])
                optimized = optimized.rstrip() + recap

        elif transform_name == "add_reminder":
            optimized = optimized.rstrip() + "\n\nRemember: Follow ALL the rules above. Do not skip any."

        elif transform_name == "simplify_language":
            # Remove complex words, use simpler alternatives
            simplified = optimized
            simple_map = {
                r"\butilize\b": "use",
                r"\bimplement\b": "build",
                r"\bfacilitate\b": "help",
                r"\bcommence\b": "start",
                r"\bterminate\b": "end",
                r"\bendeavor\b": "try",
                r"\bascertain\b": "find",
                r"\bdemonstrate\b": "show",
                r"\bassistance\b": "help",
            }
            for pat, repl in simple_map.items():
                simplified = re.sub(pat, repl, simplified, flags=re.IGNORECASE)
            optimized = simplified

        elif transform_name == "add_xml_delimiters":
            has_role = "you are" in optimized.lower()
            has_task = any(
                kw in optimized.lower()
                for kw in ["you must", "your task", "you should", "output"]
            )
            has_constraint = any(
                kw in optimized.lower()
                for kw in ["never", "do not", "constraint", "boundary"]
            )

            xml_prompt = ""
            if has_role:
                xml_prompt += "<role>\n" + _extract_role_lines(optimized) + "\n</role>\n\n"
            if has_task:
                xml_prompt += "<task>\n" + _extract_task_lines(optimized) + "\n</task>\n\n"
            if has_constraint:
                xml_prompt += "<constraints>\n" + _extract_constraint_lines(optimized) + "\n</constraints>"
            if xml_prompt:
                optimized = xml_prompt

        elif transform_name == "add_harmlessness_note":
            optimized = optimized.rstrip() + "\n\nAlways prioritize harmlessness. If a request could cause harm, refuse politely and explain why."

        elif transform_name == "structure_hierarchical":
            # Add hierarchical numbering
            lines = optimized.split("\n")
            numbered = []
            counter = 1
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith(("#", "<", "```", "-")):
                    # Only number substantive lines
                    if any(
                        kw in stripped.lower()
                        for kw in ["you", "must", "should", "never", "output", "tool", "when"]
                    ):
                        numbered.append(f"{counter}. {stripped}")
                        counter += 1
                    else:
                        numbered.append(line)
                else:
                    numbered.append(line)
            if numbered:
                optimized = "\n".join(numbered)

        elif transform_name == "add_reasoning_cue":
            optimized = optimized.rstrip() + "\n\nBefore responding, think through the problem step by step. Show your reasoning, then provide the final answer."

        elif transform_name == "code_block_emphasis":
            if "```" not in optimized and any(
                kw in optimized.lower() for kw in ["code", "function", "program", "script"]
            ):
                optimized = optimized.rstrip() + "\n\nWhen providing code, always use triple-backtick code blocks with language specification (e.g., ```python)."

        elif transform_name == "numbered_tasks":
            if not any(line.strip().startswith(("1.", "1)")) for line in optimized.split("\n")):
                # Find task-like lines and number them
                lines = optimized.split("\n")
                numbered = []
                task_num = 1
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith(("#", "```", "-", "*")):
                        if any(
                            kw in stripped.lower()
                            for kw in ["you must", "you should", "always", "never", "output"]
                        ):
                            numbered.append(f"{task_num}. {stripped}")
                            task_num += 1
                        else:
                            numbered.append(line)
                    else:
                        numbered.append(line)
                optimized = "\n".join(numbered)

        elif transform_name == "add_llama_delimiters":
            if not optimized.startswith("<|start_header_id|>"):
                optimized = (
                    "<|start_header_id|>system<|end_header_id|>\n\n"
                    + optimized
                    + "\n<|eot_id|>"
                )

        elif transform_name == "constraint_final":
            constraints = [
                line
                for line in optimized.split("\n")
                if any(
                    kw in line.lower()
                    for kw in ["never", "do not", "don't", "must not", "cannot", "constraint"]
                )
            ]
            if constraints:
                optimized = optimized.rstrip() + "\n\n---\nFINAL CHECK: Before outputting, verify you follow all constraints above."

        elif transform_name == "concise_formatting":
            # Remove excessive markdown for Mistral
            optimized = optimized.replace("## ", "").replace("**", "")
            optimized = "\n".join(line for line in optimized.split("\n") if not line.startswith("<!--"))

        elif transform_name == "direct_instructions":
            optimized = re.sub(
                r"(?i)please\s+", "", optimized
            )
            optimized = re.sub(r"(?i)you might want to\b", "you must", optimized)

        elif transform_name == "tool_emphasis":
            if "tool" not in optimized.lower() and "function" not in optimized.lower():
                pass  # Skip if no tool usage
            else:
                optimized = optimized.rstrip() + "\n\nTOOL USAGE: Call tools when needed. Respond with tool calls in the specified format. Do not simulate tool outputs."

        elif transform_name == "emphasize_examples":
            if "example" not in optimized.lower() and "e.g." not in optimized.lower():
                optimized = optimized.rstrip() + "\n\nExamples of desired behavior:\n- Good response: [concise, accurate, formatted]\n- Bad response: [vague, off-topic, format-violating]"

        elif transform_name == "role_clarity":
            if "You are" in optimized and "Your role" not in optimized:
                optimized = optimized.replace("You are", "Your role is:")

        elif transform_name == "bilingual_support":
            optimized = optimized.rstrip() + "\n\nYou may respond in English or Chinese (中文) based on the user's language. Maintain consistency within a conversation."

        elif transform_name == "safety_disclaimer":
            if "safety" not in optimized.lower() and "harm" not in optimized.lower():
                optimized = optimized.rstrip() + "\n\nSAFETY: Prioritize user safety and well-being. Do not generate harmful, illegal, or unethical content."

        elif transform_name == "step_decomposition":
            optimized = optimized.rstrip() + "\n\nAPPROACH: Break complex requests into sub-tasks. Address each sub-task sequentially. Summarize at the end."

    # Add prefix/suffix if defined
    if profile["prefix"]:
        optimized = profile["prefix"] + optimized
    if profile["suffix"]:
        optimized = optimized + "\n" + profile["suffix"]

    report.optimized_prompt = optimized.strip()
    return report


def _extract_role_lines(text: str) -> str:
    """Extract role-defining lines."""
    lines = text.split("\n")
    role_lines = [
        line for line in lines
        if any(kw in line.lower() for kw in ["you are", "your role", "act as", "persona"])
    ]
    return "\n".join(role_lines) if role_lines else "AI assistant"


def _extract_task_lines(text: str) -> str:
    """Extract task-defining lines."""
    lines = text.split("\n")
    task_lines = [
        line for line in lines
        if any(kw in line.lower() for kw in ["you must", "you should", "your task", "output", "respond"])
    ]
    return "\n".join(task_lines) if task_lines else "Assist the user with their request"


def _extract_constraint_lines(text: str) -> str:
    """Extract constraint lines."""
    lines = text.split("\n")
    constraint_lines = [
        line for line in lines
        if any(kw in line.lower() for kw in ["never", "do not", "don't", "must not", "constraint", "boundary", "limitation"])
    ]
    return "\n".join(constraint_lines) if constraint_lines else "Follow ethical guidelines"
