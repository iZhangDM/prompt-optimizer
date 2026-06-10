"""Length Optimizer — tightens prompts by removing redundancy."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class LengthReport:
    """Length optimization results."""

    original_words: int
    optimized_words: int
    words_removed: int
    reduction_pct: float
    optimized_text: str
    changes: List[Dict[str, str]] = field(default_factory=list)


# ── Redundancy patterns ──────────────────────────────────────────────

# Phrases that can be shortened
REDUNDANCY_MAP: list[tuple[str, str]] = [
    # Wordy → concise
    (r"in order to\b", "to"),
    (r"for the purpose of\b", "for"),
    (r"due to the fact that\b", "because"),
    (r"in the event that\b", "if"),
    (r"with regard to\b", "regarding"),
    (r"in terms of\b", "about"),
    (r"it is important to note that\b", "note:"),
    (r"it should be noted that\b", "note:"),
    (r"please be aware that\b", ""),
    (r"it is worth mentioning that\b", ""),
    (r"as a matter of fact\b", ""),
    (r"at this point in time\b", "now"),
    (r"at the present time\b", "now"),
    (r"in the majority of cases\b", "usually"),
    (r"a large number of\b", "many"),
    (r"a majority of\b", "most"),
    (r"a sufficient amount of\b", "enough"),
    (r"on a regular basis\b", "regularly"),
    (r"on a daily basis\b", "daily"),
    (r"in the near future\b", "soon"),
    (r"in close proximity to\b", "near"),
    (r"has the ability to\b", "can"),
    (r"has the capability to\b", "can"),
    (r"is able to\b", "can"),
    (r"is capable of\b", "can"),
    (r"make a decision\b", "decide"),
    (r"make use of\b", "use"),
    (r"take into consideration\b", "consider"),
    (r"take into account\b", "consider"),
    (r"give consideration to\b", "consider"),
    (r"provide assistance\b", "help"),
    (r"conduct an analysis\b", "analyze"),
    (r"perform an assessment\b", "assess"),
    (r"carry out\b", "do"),
    (r"with the exception of\b", "except"),
    (r"in addition to\b", "besides"),
    (r"in spite of the fact that\b", "although"),
    (r"prior to\b", "before"),
    (r"subsequent to\b", "after"),
    (r"in conjunction with\b", "with"),
    (r"as well as\b", "and"),
    (r"along with\b", "with"),
    (r"in the process of\b", ""),
    (r"the vast majority of\b", "most"),
    (r"each and every\b", "each"),
    (r"first and foremost\b", "first"),
    (r"last but not least\b", "finally"),
    (r"all of the\b", "all"),
    (r"both of the\b", "both"),
    (r"whether or not\b", "whether"),
    (r"in actual fact\b", "actually"),
    (r"absolutely essential\b", "essential"),
    (r"completely eliminate\b", "eliminate"),
    (r"totally unique\b", "unique"),
    (r"very unique\b", "unique"),
    (r"completely finish\b", "finish"),
    (r"end result\b", "result"),
    (r"final outcome\b", "outcome"),
    (r"past history\b", "history"),
    (r"future plans\b", "plans"),
    (r"advance planning\b", "planning"),
    (r"basic fundamentals\b", "fundamentals"),
    (r"brief summary\b", "summary"),
    (r"brief moment\b", "moment"),
    (r"consensus of opinion\b", "consensus"),
    (r"current trend\b", "trend"),
    (r"exact same\b", "same"),
    (r"free gift\b", "gift"),
    (r"new innovation\b", "innovation"),
    (r"personal opinion\b", "opinion"),
    (r"repeat again\b", "repeat"),
    (r"return back\b", "return"),
    (r"safe haven\b", "haven"),
    (r"unexpected surprise\b", "surprise"),
    (r"usual custom\b", "custom"),
    (r"still remains\b", "remains"),
    (r"continue on\b", "continue"),
    (r"join together\b", "join"),
    (r"merge together\b", "merge"),
    # Hedging language — optional removal
    (r"I think that\b", ""),
    (r"I believe that\b", ""),
    (r"in my opinion,?\s*", ""),
    (r"it seems that\b", ""),
    (r"it appears that\b", ""),
    (r"arguably,?\s*", ""),
    # Filler
    (r"needless to say,?\s*", ""),
    (r"it goes without saying that\b", ""),
    (r"that being said,?\s*", ""),
    # Polite padding
    (r"please feel free to\b", "please"),
    (r"you are welcome to\b", "you can"),
    (r"don't hesitate to\b", "please"),
    (r"at your earliest convenience\b", "soon"),
    (r"thank you in advance\b", ""),
    (r"thanks in advance\b", ""),
    (r"I would appreciate it if you could\b", "please"),
    (r"I would like to\b", "I will"),
]


def optimize_length(text: str) -> LengthReport:
    """Apply redundancy reductions and return the optimized text."""
    original_words = len(text.split())
    optimized = text
    changes: list[dict[str, str]] = []

    for pattern, replacement in REDUNDANCY_MAP:
        compiled = re.compile(pattern, re.IGNORECASE)
        if compiled.search(optimized):
            optimized, count = compiled.subn(replacement, optimized)
            if count > 0:
                changes.append(
                    {
                        "pattern": pattern,
                        "replacement": replacement if replacement else "(removed)",
                        "matches": str(count),
                    }
                )

    # Collapse multiple blank lines
    optimized = re.sub(r"\n{3,}", "\n\n", optimized)

    # Collapse multiple spaces (but not newlines)
    optimized = re.sub(r"[ \t]{2,}", " ", optimized)

    # Trim trailing whitespace on each line
    optimized = "\n".join(line.rstrip() for line in optimized.split("\n"))

    optimized_words = len(optimized.split())
    words_removed = original_words - optimized_words
    reduction_pct = (words_removed / original_words * 100) if original_words > 0 else 0.0

    return LengthReport(
        original_words=original_words,
        optimized_words=optimized_words,
        words_removed=words_removed,
        reduction_pct=round(reduction_pct, 1),
        optimized_text=optimized.strip(),
        changes=changes,
    )
