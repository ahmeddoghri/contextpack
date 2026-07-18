# 📦 contextpack

**Shrink a prompt without shrinking the answer.**

![CI](https://github.com/ahmeddoghri/contextpack/actions/workflows/ci.yml/badge.svg)
![tests](https://img.shields.io/badge/tests-10%20passing-brightgreen)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![deps](https://img.shields.io/badge/runtime%20deps-none-success)
![license](https://img.shields.io/badge/license-MIT-black)

> **Compress a document to 50% of its length and every load-bearing fact still
> survives. Push past that and recall starts to drop, which is exactly the
> tradeoff you need to see.** `python -m contextpack.eval`.

Long context costs you twice. You pay per token to send it, and you pay in
latency for every token the model has to read before it can answer. The
LLMLingua line of work (Jiang et al., 2023) showed you can compress a prompt 2
to 5x by dropping the tokens a language model finds highly predictable, the
ones that add length without adding information, while keeping the tokens that
actually carry content.

contextpack implements that idea with a transparent scoring proxy instead of a
real perplexity model: function words and repeated phrases score low and go
first, numbers and specific terms score high and stay. No model, no network,
no dependencies, and every scoring rule is a few lines you can read.

The part most compression demos skip: measuring whether it actually worked.
Hitting a target ratio is easy. Keeping the facts an answer depends on is the
real job, so this ships a benchmark that checks exactly that.

---

## The result in one command

```bash
python -m contextpack.eval
```
```
compression benchmark: 145-word document, 5 questions, 10 load-bearing keywords

    target  actual ratio   tokens saved  keyword recall
     100%         100%              0           100%
      70%          70%             43           100%
      50%          50%             73           100%
      35%          35%             94            80%
      25%          25%           109            80%
      15%          15%           123            70%

you can compress to 50% of the original (73 tokens saved) and still keep every load-bearing keyword.
```

That knee in the curve is the entire point. Compression to 50% is free: every
number, name, and term the sample questions need is still there. Push past that
and the compressor starts cutting into content it can no longer distinguish
from filler, and recall degrades. Knowing where your knee is, instead of
picking a compression ratio by feel, is the whole value here.

## Install

```bash
git clone https://github.com/ahmeddoghri/contextpack
cd contextpack && pip install -e .
python examples/quickstart.py
```

## Use it

```python
from contextpack.compress import Compressor
from contextpack.score import keyword_recall

compressor = Compressor(target_ratio=0.5)
result = compressor.compress(long_prompt)

print(result.compressed)             # the shrunk prompt, ready to send
print(result.tokens_saved)           # how many tokens you did not pay for
print(result.compression_ratio)      # 0.5

# check that the facts you actually need survived
recall = keyword_recall(result.compressed, ["invoice_number", "412", "Rotterdam"])
print(recall)   # 1.0 means every one of those tokens made it through
```

## How the scoring works

Every token gets a "surprise" score. Low surprise means the compressor thinks a
language model would have predicted this token anyway, so removing it costs
little. High surprise means the token is specific enough that removing it would
actually change the meaning.

```
start at surprise = 1.0
  common function word (the, is, of, and, ...)  -> surprise -0.7
  repeated a nearby word                        -> surprise -0.4
  contains a digit                              -> surprise +0.5
  long, specific word (8+ characters)           -> surprise +0.2

keep the highest-surprise tokens up to the target budget,
drop the rest, reassemble in original order
```

This is a coarse proxy for real perplexity-based scoring, not a replacement for
it. It captures the same core idea (predictable tokens compress away, specific
ones do not) with zero model calls, which is exactly what you want for a
transparent, reproducible demo. Swap in a real small-model perplexity scorer at
the `_score_tokens` seam for production use.

## Tests

```bash
pip install pytest && pytest -q      # 10 passing
```

## License

MIT © Ahmed Doghri
