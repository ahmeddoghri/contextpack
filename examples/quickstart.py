"""Sixty-second tour of contextpack.

    python examples/quickstart.py
"""
from contextpack.compress import Compressor
from contextpack.score import keyword_recall

text = (
    "In accordance with the terms outlined in this agreement, it is "
    "important to note that the vendor shall deliver 412 units of the "
    "RX9000 sensor to Rotterdam no later than March 15th."
)

compressor = Compressor(target_ratio=0.5)
result = compressor.compress(text)

print(f"original:   {result.original_tokens} tokens")
print(f"compressed: {result.compressed_tokens} tokens ({result.compression_ratio:.0%})")
print(f"text:       {result.compressed}")
print(f"recall:     {keyword_recall(result.compressed, ['412', 'RX9000', 'Rotterdam']):.0%}")
