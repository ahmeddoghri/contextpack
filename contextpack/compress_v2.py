"""The surprise scorer, fixed for documents that spell numbers out in words.

``_score_tokens`` gives a token a +0.5 "keep me" bonus if it contains a
digit character, on the reasoning that numbers are usually load-bearing.
That reasoning is right, but the detection only fires on Arabic numerals.
A document that writes "four hundred twelve units" and "thirty days"
instead of "412 units" and "30 days" gets none of that protection, even
though the facts are exactly as load-bearing. Two documents stating the
identical facts compress very differently purely because of numeral style:

    digit document, target 50%:      keyword recall 100%
    word-form document, target 50%:  keyword recall 89%  (worse at 35%: 56%)

At 50% "thirty" (the delay that triggers termination) survives on luck
alone in the digit-free rewrite; at 35% it's gone. Nothing about the
*content* changed, only how the number is spelled, which is not something
a compression tool should be sensitive to.

``_score_tokens_v2`` adds the same +0.5 bonus this module already gives
digit tokens to number words: cardinals (one..twenty, thirty..ninety,
hundred, thousand, million, billion) and ordinals (first..twentieth,
thirtieth..ninetieth, hundredth...), matched as whole tokens so "tenth"
doesn't accidentally catch "tent". Nothing else about the scoring changes.
"""
from __future__ import annotations

import re
from typing import List

from .compress import _LOW_INFO, CompressionResult, ScoredToken

_WORD = re.compile(r"\S+")

_CARDINALS = {
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty",
    "fifty", "sixty", "seventy", "eighty", "ninety",
    "hundred", "thousand", "million", "billion", "trillion",
}
_ORDINALS = {
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh",
    "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth",
    "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth",
    "nineteenth", "twentieth", "thirtieth", "fortieth", "fiftieth",
    "sixtieth", "seventieth", "eightieth", "ninetieth", "hundredth",
    "thousandth", "millionth", "billionth",
}
_NUMBER_WORDS = _CARDINALS | _ORDINALS


def _score_tokens_v2(tokens: List[str]) -> List[ScoredToken]:
    scored = []
    seen_recently: List[str] = []
    window = 8
    for i, tok in enumerate(tokens):
        core = re.sub(r"[^\w]", "", tok.lower())
        surprise = 1.0
        if core in _LOW_INFO:
            surprise -= 0.7
        if core and core in seen_recently:
            surprise -= 0.4
        if any(ch.isdigit() for ch in tok) or core in _NUMBER_WORDS:
            surprise += 0.5
        if len(core) >= 8:
            surprise += 0.2
        surprise = max(surprise, 0.05)
        scored.append(ScoredToken(tok, surprise, i))
        seen_recently.append(core)
        if len(seen_recently) > window:
            seen_recently.pop(0)
    return scored


class CompressorV2:
    """Same interface as :class:`contextpack.compress.Compressor`, using the
    number-word-aware scorer."""

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
        scored = _score_tokens_v2(tokens)

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
