from contextpack.compress import Compressor
from contextpack.corpus import DOCUMENT, QUESTIONS
from contextpack.score import keyword_recall, normalize


def test_corpus_keywords_actually_appear():
    # guards against a corpus bug: every keyword must be a real token in DOCUMENT
    present = normalize(DOCUMENT)
    for question, keywords in QUESTIONS:
        for kw in keywords:
            assert kw.lower() in present, f"{kw!r} for {question!r} not found in DOCUMENT"


def test_compression_hits_target_ratio():
    c = Compressor(target_ratio=0.5)
    r = c.compress(DOCUMENT)
    n = len(DOCUMENT.split())
    assert abs(r.compressed_tokens - round(n * 0.5)) <= 1


def test_full_ratio_keeps_everything():
    c = Compressor(target_ratio=1.0)
    r = c.compress(DOCUMENT)
    assert r.compressed_tokens == r.original_tokens
    assert r.dropped_tokens == []


def test_tokens_saved_is_correct():
    c = Compressor(target_ratio=0.4)
    r = c.compress(DOCUMENT)
    assert r.tokens_saved == r.original_tokens - r.compressed_tokens


def test_invalid_ratio_rejected():
    import pytest
    with pytest.raises(ValueError):
        Compressor(target_ratio=0.0)
    with pytest.raises(ValueError):
        Compressor(target_ratio=1.5)


def test_numbers_survive_aggressive_compression():
    # numbers are scored as high-surprise, so they should survive even at 20%
    c = Compressor(target_ratio=0.2)
    r = c.compress(DOCUMENT)
    kept = normalize(r.compressed)
    assert "412" in kept
    assert "rotterdam" in kept


def test_keyword_recall_full_text():
    all_keywords = [kw for _, kws in QUESTIONS for kw in kws]
    assert keyword_recall(DOCUMENT, all_keywords) == 1.0


def test_keyword_recall_empty_required_is_perfect():
    assert keyword_recall("anything", []) == 1.0


def test_keyword_recall_partial():
    assert keyword_recall("the cat sat", ["cat", "dog"]) == 0.5


def test_moderate_compression_keeps_full_recall():
    all_keywords = [kw for _, kws in QUESTIONS for kw in kws]
    c = Compressor(target_ratio=0.5)
    r = c.compress(DOCUMENT)
    assert keyword_recall(r.compressed, all_keywords) == 1.0
