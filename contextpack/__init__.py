"""contextpack: shrink a prompt without shrinking the answer.

Long context is expensive twice over: you pay for every token you send, and you
pay in latency for every token the model has to attend over. The LLMLingua line
of work (Jiang et al., 2023) showed you can compress a prompt by 2 to 5x by
dropping the low-information tokens (the ones a language model finds highly
predictable, and therefore redundant) while keeping the tokens that actually
carry the content.

This package implements that idea with a transparent, dependency-free perplexity
proxy instead of a real language model: a token's "surprise" is approximated by
how rare it is and how much it repeats its neighbors. Drop the least surprising
tokens first, keep compressing until you hit your budget, and measure how much
of the original meaning survives with a keyword-recall check against the source.

It ships a benchmark that reports compression ratio versus answer-keyword
retention, so the tradeoff is a number, not a feeling.
"""
from contextpack.compress import CompressionResult, Compressor
from contextpack.score import keyword_recall

__all__ = ["Compressor", "CompressionResult", "keyword_recall"]

__version__ = "0.1.0"
