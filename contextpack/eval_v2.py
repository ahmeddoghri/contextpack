"""Does the compressor's "keep the numbers" heuristic survive prose numerals?

``contextpack.eval`` reports a compression knee point (50% keeps 100% of
load-bearing keywords) on a document that writes every number as an
Arabic numeral. The scorer's protection for numbers is a digit-character
check, so a document that spells numbers out in words ("thirty days"
instead of "30 days") gets none of it, even though the facts are exactly
as load-bearing.

This module reruns the same keyword-recall sweep against
:mod:`contextpack.adversarial`'s word-form documents (a fact-for-fact
restatement of the bundled document, plus an independently-written
holdout document in a different domain) for both the original
``Compressor`` and the number-word-aware ``CompressorV2``.

    python -m contextpack.eval_v2
"""
from __future__ import annotations

import argparse
import json
from typing import Dict, Sequence

from .adversarial import (
    ADVERSARIAL_DOCUMENT,
    ADVERSARIAL_QUESTIONS,
    HOLDOUT_DOCUMENT,
    HOLDOUT_QUESTIONS,
)
from .compress import Compressor
from .compress_v2 import CompressorV2
from .score import keyword_recall

RATIOS = (1.0, 0.7, 0.5, 0.35)


def _sweep(document: str, questions: Sequence[tuple], compressor_cls) -> Dict[float, float]:
    all_kw = [kw for _, kws in questions for kw in kws]
    return {
        ratio: round(keyword_recall(compressor_cls(ratio).compress(document).compressed, all_kw), 4)
        for ratio in RATIOS
    }


def build_report() -> Dict:
    return {
        "adversarial": {
            "v1": _sweep(ADVERSARIAL_DOCUMENT, ADVERSARIAL_QUESTIONS, Compressor),
            "v2": _sweep(ADVERSARIAL_DOCUMENT, ADVERSARIAL_QUESTIONS, CompressorV2),
        },
        "holdout": {
            "v1": _sweep(HOLDOUT_DOCUMENT, HOLDOUT_QUESTIONS, Compressor),
            "v2": _sweep(HOLDOUT_DOCUMENT, HOLDOUT_QUESTIONS, CompressorV2),
        },
    }


def format_report(report: Dict) -> str:
    lines = [
        "keyword recall on word-form (spelled-out) numbers, by compression ratio",
        "=" * 66,
        f"{'corpus / version':<22}" + "".join(f"{r:>11.0%}" for r in RATIOS),
        "-" * 66,
    ]
    for corpus_name in ("adversarial", "holdout"):
        for v in ("v1", "v2"):
            row = report[corpus_name][v]
            lines.append(f"{corpus_name + ' / ' + v:<22}" + "".join(f"{row[r]:>11.0%}" for r in RATIOS))
        lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", default=None)
    args = parser.parse_args(argv)

    report = build_report()
    print(format_report(report))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
