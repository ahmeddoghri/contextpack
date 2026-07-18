"""Compress a prompt by dropping its least informative tokens.

The real LLMLingua approach scores each token's information content with a
small language model's perplexity: a token the model finds highly predictable
given its context contributes little if you remove it, because the model could
have guessed it anyway. We approximate that signal without a model:

  - common words (stopwords, filler) are cheap to predict, drop first
  - a word that just repeated a nearby word is redundant, drop it
  - rare, specific words (numbers, names, technical terms) are the content,
    keep them

This is a coarser signal than a real perplexity model, but it is transparent,
free, and it captures the same core idea: predictable tokens compress away,
surprising tokens do not.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_WORD = re.compile(r"\S+")

# Cheap-to-predict function words. Dropping these first is most of the
# compression budget in ordinary English text, and it is exactly what
# perplexity-based scoring finds too: function words are highly predictable.
_LOW_INFO = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "of", "to", "in", "on", "at", "for", "with", "and", "or", "but", "so",
    "that", "this", "these", "those", "it", "its", "as", "by", "from",
    "than", "then", "there", "here", "which", "who", "whom", "very",
    "just", "also", "such", "some", "any", "will", "would", "could",
    "should", "can", "may", "might", "do", "does", "did", "has", "have",
    "had", "not", "no", "we", "you", "they", "i", "he", "she",
}


@dataclass
class ScoredToken:
    text: str
    surprise: float   # higher = more informative, keep it
    index: int


@dataclass
class CompressionResult:
    original: str
    compressed: str
    original_tokens: int
    compressed_tokens: int
    dropped_tokens: list[str] = field(default_factory=list)

    @property
    def compression_ratio(self) -> float:
        if self.original_tokens == 0:
            return 1.0
        return self.compressed_tokens / self.original_tokens

    @property
    def tokens_saved(self) -> int:
        return self.original_tokens - self.compressed_tokens


def _score_tokens(tokens: list[str]) -> list[ScoredToken]:
    scored = []
    seen_recently: list[str] = []
    window = 8
    for i, tok in enumerate(tokens):
        core = re.sub(r"[^\w]", "", tok.lower())
        surprise = 1.0
        if core in _LOW_INFO:
            surprise -= 0.7
        if core and core in seen_recently:
            surprise -= 0.4   # repeated recently: redundant, low new information
        if any(ch.isdigit() for ch in tok):
            surprise += 0.5   # numbers are usually load-bearing
        if len(core) >= 8:
            surprise += 0.2   # long, specific words carry more content
        surprise = max(surprise, 0.05)
        scored.append(ScoredToken(tok, surprise, i))
        seen_recently.append(core)
        if len(seen_recently) > window:
            seen_recently.pop(0)
    return scored


class Compressor:
    """Compress text to a target token budget by dropping low-surprise tokens.

    ``target_ratio`` is the fraction of the original token count to keep, e.g.
    0.5 keeps roughly half. Tokens are dropped in ascending order of surprise
    (least informative first) until the target is hit, then reassembled in
    their original order so the result still reads left to right.
    """

    def __init__(self, target_ratio: float = 0.5) -> None:
        if not 0.0 < target_ratio <= 1.0:
            raise ValueError("target_ratio must be in (0, 1]")
        self.target_ratio = target_ratio

    def compress(self, text: str) -> CompressionResult:
        tokens = _WORD.findall(text)
        n = len(tokens)
        if n == 0:
            return CompressionResult(text, text, 0, 0)

        target_count = max(1, round(n * self.target_ratio))
        scored = _score_tokens(tokens)

        # keep the highest-surprise tokens up to the budget, preserving order
        keep_indices = {
            t.index for t in sorted(scored, key=lambda t: t.surprise, reverse=True)[:target_count]
        }
        kept = [t.text for t in scored if t.index in keep_indices]
        dropped = [t.text for t in scored if t.index not in keep_indices]

        return CompressionResult(
            original=text,
            compressed=" ".join(kept),
            original_tokens=n,
            compressed_tokens=len(kept),
            dropped_tokens=dropped,
        )
