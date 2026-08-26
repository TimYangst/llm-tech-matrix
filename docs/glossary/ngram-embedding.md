# N-gram Embedding

> 中文版：[ngram-embedding.zh.md](./ngram-embedding.zh.md)

**Slug:** `ngram-embedding`
**Category:** other
**One-line:** A large embedding table keyed by short n-grams rather than single tokens, adding parameters at near-zero per-token FLOPs — and, because addressing is deterministic, cheap enough to hold in host memory and prefetch.
**First introduced in:** No single origin. The n-gram-keyed form generalizes unigram lookup and has a long lineage; the modern "scale capacity via offloadable embedding tables" framing is associated with per-layer / offloaded embedding work (Google DeepMind, 2025) and follow-ups (Cheng et al., 2026). Qwen's implementation is documented in [On the Design of Qwen3.8-Next Architecture (Qwen Team, 2026)](https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf) §2.3.

## Description

MoE scales parameters by adding experts, but every added expert still costs accelerator
memory and its routing costs bandwidth. Embedding tables scale parameters along a
different axis: a lookup is not a matmul, so capacity grows with **negligible additional
per-token FLOPs**. And because the address is computed from the input tokens rather than
from activations, the lookup is *deterministic and knowable in advance* — which is what
makes it safe to keep the table in host memory and prefetch it asynchronously while the
accelerator computes earlier layers.

N-gram embeddings generalize the ordinary unigram embedding by keying on the short n-gram
*ending at* each token instead of on token identity alone, so the retrieved vector is
conditioned on local context. The retrieved vectors augment the token representation at one
chosen layer.

What makes this entry worth reading is that Qwen's ablations are unusually candid about the
limits:

- **Placement is nearly free to choose.** No depth regime dominates; the first two layers
  are strongest, but intermediate and deep placements stay competitive, and placement is
  largely insensitive to the attention mechanism. Qwen picks **layer 2 specifically so the
  host-memory prefetch overlaps layer 1's computation** — an infrastructure reason, not a
  quality one.
- **One layer is enough.** Splitting the same parameter budget across multiple layers gives
  no consistent benefit.
- **Loss and benchmarks disagree, sharply.** Scaling the n-gram vocabulary from 20× to 200×
  the base tokenizer vocabulary lowers loss *monotonically* while downstream accuracy
  saturates or fluctuates. Anyone tuning this on loss alone would over-scale the table.
- **Chinese benchmarks are the exception** — C-Eval and CMMLU improve consistently with
  vocabulary size, where other benchmarks plateau.
- **It is not a substitute for MoE.** Under a *fixed* total parameter budget, trading experts
  for n-gram slots puts the loss optimum around 10× vocabulary (25% of params) but shows no
  clear downstream gain over the MoE-only baseline. The report's conclusion is that "N-gram
  embeddings and MoE experts play distinct roles in scaling capacity" — so the honest way to
  use n-gram tables is as *additional* parameters, not reallocated ones.

Qwen also reports a set of parameter-efficiency tricks that **did not work** in their recipe:
token normalization for vocabulary compression, non-uniform allocation across n-gram orders,
and frequency-based partitioning of embedding slots. Negative results at this level of
specificity are rare and worth keeping.

## Reference materials

- Original paper: <https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf> (§2.3)
- Reference implementation: — (config keys `ngram_size`, `ngram_vocab_size_base`, `heads_per_ngram`, `ple_layer_ids`)

## Used by

| Model | Variation / details |
| ----- | ------------------- |
| Qwen3.8-Flash-Next | A **single** n-gram embedding layer at **layer 2**, holding **51B parameters** in a 20,000,000-entry table (`ngram_size=3` — bigrams/trigrams, `heads_per_ngram=8`, embed dim 2560, depthwise conv kernel 4, `split_ngram_parts=128`). Tables are held **off-accelerator in host memory and asynchronously prefetched**, so the 51B is reported separately from the 125B backbone total. Trained with Adam, weight decay disabled; the layer's key/value projections are on [Muon](./muon.md). |

## Related techniques

- [DeepSeekMoE](./deepseekmoe.md) — the other capacity-scaling axis, which this is explicitly *not* a substitute for.
- [Stable LatentMoE](./latentmoe.md) — Kimi K3's approach to making the expert axis cheaper, for contrast: it compresses where experts live rather than moving capacity out of the backbone entirely.
