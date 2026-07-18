"""Benchmark: how much can you compress before the answer-critical content
starts disappearing?

We compress a realistic, wordy document at several target ratios and measure
keyword recall against a set of questions whose answers depend on specific
tokens (numbers, names, terms) in the source. That is the real tradeoff curve:
how far can you push compression before the facts an answer needs start
dropping out.

Run it:

    python -m contextpack.eval

Deterministic. Pure stdlib, no model, no network.
"""
from __future__ import annotations

from contextpack.compress import Compressor
from contextpack.corpus import DOCUMENT, QUESTIONS
from contextpack.score import keyword_recall


def run() -> None:
    ratios = [1.0, 0.7, 0.5, 0.35, 0.25, 0.15]
    all_keywords = [kw for _, kws in QUESTIONS for kw in kws]

    print(f"compression benchmark: {len(DOCUMENT.split())}-word document, "
          f"{len(QUESTIONS)} questions, {len(all_keywords)} load-bearing keywords\n")
    print(f"  {'target':>8}  {'actual ratio':>12}  {'tokens saved':>13}  {'keyword recall':>14}")

    results = []
    for ratio in ratios:
        c = Compressor(target_ratio=ratio)
        result = c.compress(DOCUMENT)
        recall = keyword_recall(result.compressed, all_keywords)
        results.append((ratio, result, recall))
        print(f"  {ratio:>7.0%}  {result.compression_ratio:>11.0%}  "
              f"{result.tokens_saved:>13}  {recall:>13.0%}")

    # find the tightest ratio that still keeps recall at 100%
    perfect = [r for r in results if r[2] == 1.0]
    if perfect:
        best_ratio, best_result, _ = min(perfect, key=lambda r: r[0])
        print(f"\nyou can compress to {best_result.compression_ratio:.0%} of the "
              f"original ({best_result.tokens_saved} tokens saved) and still keep "
              f"every load-bearing keyword.")
    print("\npast that point, recall drops because the compressor starts cutting")
    print("into content it can no longer tell apart from filler. that knee in the")
    print("curve is the real number: not 'how small can I make this' but 'how")
    print("small can I make this before the answer breaks'.")


if __name__ == "__main__":
    run()
