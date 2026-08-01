"""Tests for the digit-only number bias and its fix."""

from __future__ import annotations

from contextpack.adversarial import (
    ADVERSARIAL_DOCUMENT,
    ADVERSARIAL_QUESTIONS,
    HOLDOUT_DOCUMENT,
    HOLDOUT_QUESTIONS,
)
from contextpack.compress import Compressor
from contextpack.compress_v2 import CompressorV2
from contextpack.corpus import DOCUMENT, QUESTIONS
from contextpack.eval_v2 import build_report
from contextpack.score import keyword_recall, normalize

_ALL_KW_ADV = [kw for _, kws in ADVERSARIAL_QUESTIONS for kw in kws]
_ALL_KW_ORIG = [kw for _, kws in QUESTIONS for kw in kws]


# --- the finding: number words get none of the digit protection ------------

def test_adversarial_corpus_restates_the_same_facts():
    """Sanity check: the word-form document is a true restatement, not a
    different, easier-to-compress document."""
    for kw in ("rotterdam", "march", "meridian", "rx9000"):
        assert kw in normalize(ADVERSARIAL_DOCUMENT)


def test_original_compressor_loses_recall_on_word_form_numbers():
    """The same 50% ratio that keeps 100% recall on the digit document loses
    load-bearing facts on the word-form restatement of identical content."""
    r_digit = Compressor(0.5).compress(DOCUMENT)
    r_words = Compressor(0.5).compress(ADVERSARIAL_DOCUMENT)
    assert keyword_recall(r_digit.compressed, _ALL_KW_ORIG) == 1.0
    assert keyword_recall(r_words.compressed, _ALL_KW_ADV) < 1.0


def test_thirty_days_is_dropped_by_the_original_scorer_at_50_percent():
    r = Compressor(0.5).compress(ADVERSARIAL_DOCUMENT)
    assert "thirty" not in normalize(r.compressed)


# --- the fix -----------------------------------------------------------------

def test_fixed_compressor_restores_full_recall_at_the_knee_ratio():
    r = CompressorV2(0.5).compress(ADVERSARIAL_DOCUMENT)
    assert keyword_recall(r.compressed, _ALL_KW_ADV) == 1.0


def test_fixed_compressor_keeps_thirty_days():
    r = CompressorV2(0.5).compress(ADVERSARIAL_DOCUMENT)
    assert "thirty" in normalize(r.compressed)


def test_fixed_compressor_improves_over_original_at_every_ratio():
    for ratio in (0.5, 0.35):
        r1 = Compressor(ratio).compress(ADVERSARIAL_DOCUMENT)
        r2 = CompressorV2(ratio).compress(ADVERSARIAL_DOCUMENT)
        assert keyword_recall(r2.compressed, _ALL_KW_ADV) >= keyword_recall(
            r1.compressed, _ALL_KW_ADV
        )


def test_number_word_detection_does_not_misfire_on_lookalikes():
    """"tenth" is a number word; "tent" and "tender" are not, and must not
    get the bonus by accident."""
    from contextpack.compress_v2 import _NUMBER_WORDS

    assert "tenth" in _NUMBER_WORDS
    assert "tent" not in _NUMBER_WORDS
    assert "tender" not in _NUMBER_WORDS


# --- the fix does not regress the original digit-numeral benchmark ---------

def test_fixed_compressor_reproduces_original_recall_exactly():
    for ratio in (1.0, 0.7, 0.5, 0.35, 0.25, 0.15):
        r1 = Compressor(ratio).compress(DOCUMENT)
        r2 = CompressorV2(ratio).compress(DOCUMENT)
        assert keyword_recall(r1.compressed, _ALL_KW_ORIG) == keyword_recall(
            r2.compressed, _ALL_KW_ORIG
        )


# --- held out, evaluated once ------------------------------------------------

def test_holdout_is_a_different_document_and_domain():
    assert HOLDOUT_DOCUMENT != ADVERSARIAL_DOCUMENT
    assert "priya" in normalize(HOLDOUT_DOCUMENT)


def test_holdout_fix_never_regresses_recall():
    all_kw = [kw for _, kws in HOLDOUT_QUESTIONS for kw in kws]
    for ratio in (0.5, 0.35):
        r1 = Compressor(ratio).compress(HOLDOUT_DOCUMENT)
        r2 = CompressorV2(ratio).compress(HOLDOUT_DOCUMENT)
        assert keyword_recall(r2.compressed, all_kw) >= keyword_recall(r1.compressed, all_kw)


# --- the original module is untouched ---------------------------------------

def test_original_compress_module_untouched():
    import contextpack.compress as compress_module

    assert not hasattr(compress_module, "CompressorV2")


def test_original_benchmark_still_reproduces():
    r = Compressor(0.5).compress(DOCUMENT)
    assert keyword_recall(r.compressed, _ALL_KW_ORIG) == 1.0
    r35 = Compressor(0.35).compress(DOCUMENT)
    assert keyword_recall(r35.compressed, _ALL_KW_ORIG) == 0.8


# --- the full report ---------------------------------------------------------

def test_report_is_reproducible():
    assert build_report() == build_report()
