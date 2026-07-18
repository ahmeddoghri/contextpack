"""Measure how much of the content that matters survived compression.

Compression ratio alone is a vanity number: you can hit 10% of the original
length by keeping ten random words. The metric that matters is whether the
tokens an answer actually depends on are still there. We check that with
keyword recall: given a set of ground-truth keywords a downstream question
needs, what fraction survived the compression.
"""
from __future__ import annotations

import re

_WORD = re.compile(r"[a-z0-9]+")


def normalize(text: str) -> set[str]:
    """Lowercase word-token set, used for exact keyword membership checks."""
    return set(_WORD.findall(text.lower()))


def keyword_recall(compressed_text: str, required_keywords: list[str]) -> float:
    """Fraction of ``required_keywords`` present (case-insensitively) in the
    compressed text. 1.0 means every load-bearing fact survived compression."""
    if not required_keywords:
        return 1.0
    present = normalize(compressed_text)
    hits = sum(1 for kw in required_keywords if kw.lower() in present)
    return hits / len(required_keywords)
