# Dual Chunk Attention (DCA)

**Slug:** `dual-chunk-attention`
**Category:** position-embedding
**One-line:** A training-free long-context extension method that re-indexes positions inside and across fixed-size chunks so a model trained at length T can attend over sequences of length kT without retraining, typically combined with a frequency-scaling method like YaRN.
**First introduced in:** [Training-Free Long-Context Scaling of Large Language Models (An et al., 2024)](https://arxiv.org/abs/2402.17463)

## Description

Naïve RoPE-based context extension fails at very long sequences because positional
indices grow far beyond what the rotary embeddings were trained on. DCA observes
that the *relative* positions inside a chunk and *between* chunks can be re-mapped
to indices that the model has actually seen during training, giving the model a
meaningful position signal everywhere without any fine-tuning.

Concretely, sequences are partitioned into chunks of size W (close to the trained
context length), and three position indexings are used: intra-chunk (positions
within a chunk), inter-chunk (positions between chunks), and a successor index
that handles the boundary between the current chunk and recent past. Each kind
of index is mapped into a sub-range the model has seen, so attention scores stay
in-distribution.

In production, DCA is usually paired with YaRN: YaRN handles frequency-band
interpolation while DCA handles raw position re-indexing. Together they recover
near-trained-quality at multiplicative context extensions (e.g. 4×) with no
additional training.

## Reference materials

- Original paper: <https://arxiv.org/abs/2402.17463>

## Used by

| Model | Variation / details |
|---|---|
| Qwen3-32B | DCA + YaRN at deployment lifts the trained 32K context to 128K (4× extension). Applied at inference (vLLM/SGLang configs); not baked into HF `config.json` (`rope_scaling=null`). |
| Qwen3-235B-A22B | Same DCA + YaRN deployment recipe as the rest of the Qwen3 family above 1.7B. |

## Related techniques

- [YaRN RoPE scaling](./yarn-rope.md) — DCA is typically stacked with YaRN for full long-context recovery
