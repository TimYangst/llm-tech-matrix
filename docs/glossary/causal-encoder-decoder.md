# Causal Encoder-Decoder (CED)

> 中文版：[causal-encoder-decoder.zh.md](./causal-encoder-decoder.zh.md)

**Slug:** `causal-encoder-decoder`
**Category:** attention
**One-line:** Split a decoder-only stack in half so the upper half's *global* KV cache is projected from the lower half's final hidden state — prefill only has to run the lower half, so roughly half the parameters are active per prompt token versus per generated token.
**First introduced in:** [DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression (DeepSeek-AI, 2026)](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/dba1be0a40aa45a94ad051997016db3960a90277/DeepSeek_V41_Tech_Report.pdf) §2.2, "inspired by YOCO" (Sun et al., 2024).

## Description

Agentic workloads are input-heavy: every tool call returns text that has to be prefilled,
and cache misses make that prefill expensive. YOCO reduced prefill by letting the upper half
of the layers directly share the KV cache produced by the lower half. CED keeps that idea
but, per the report, adds structural changes "to enhance both the overall KV cache capacity
and the computational depth of KV generation".

The bottom `L/2` layers are the **causal encoder**. For **global** attention, each decoder
layer `l > L/2` does not derive KV from its own hidden state; its KV entries `C_l` and
compression weights `Z_l` are projected from the final encoder hidden state `H_{L/2}` with
layer-dependent weights: `C_l = H_{L/2} W^KV_l`, `Z_l = H_{L/2} W^Z_l`. The decoder's global
KV for the whole prompt can therefore be obtained by running only the encoder. The report
gives prefill complexity as going from `O(NL)` to about `O(NL/2)`.

For **sliding-window** attention, CED deliberately does *not* share: every layer, including
decoder layers, computes local KV from its own hidden state. That preserves depth in local
KV generation, but it means the first decode steps would need decoder SWA KV that exactly
requires replaying `n_win × L/2` prompt tokens through the decoder. CED resolves this with
**SWA Bounded Replay**:

- **Decoder SWA Bounded Replay** — at every prefill, replay only the last `n_win` prompt
  tokens through the decoder, with SWA truncated to that replay segment. The resulting
  states are approximate; the report finds "only a negligible impact on response quality",
  and simulates the same replay during post-training for train-aware adaptation.
- **Encoder SWA Bounded Replay** — on a prefix-cache hit whose SWA KV has been evicted,
  replay only the last `n_win` tokens of the cached prefix to regenerate SWA KV. This makes
  prefix caching depend only on global KV, so SWA KV can be dropped from the persistent
  (SSD) cache entirely.

The report flags "approximate state reconstruction in SWA Bounded Replay" as one of the
model's uncharacterized robustness boundaries.

## Reference materials

- Original paper: DeepSeek-V4.1-Flash technical report §2.2, §3.2.1 (persistent KV cache management), §3.2.2 (SWA Bounded Replay)
- Reference implementation: <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/tree/main/inference>
- Relevant blog/post: <https://api-docs.deepseek.com/news/news260910/> ("Asymmetric architecture … just 8B active parameters for input, 16B for output")

## Used by

| Model               | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4.1-Flash | 40 layers = 20-layer encoder (0–19) + 20-layer decoder (20–39); **8B active per token in prefill, 16B in decode**. Paired with [CSA2](./csa2.md), so only the decoder's Full-Mode layer (20) materializes decoder global KV from the encoder output. `n_win=128`. Persistent KV cache is ~1/8 of DeepSeek-V4's: SWA KV is no longer persisted (it moves to a host-DRAM pool of 10% of each machine's memory with a minutes-scale TTL, falling back to Encoder SWA Bounded Replay on a miss), and global KV is ~1/4 of V4's. Global KV stays in the persistent cache with a guaranteed lifetime of at least 72 hours. |

## Related techniques

- [Compressed Sparse Attention 2 (CSA2)](./csa2.md) — the cross-layer KV/index sharing scheme CED is combined with in V4.1.
- [CSA + HCA](./csa-hca.md) — the DeepSeek-V4 attention stack, whose SWA persistence cost Bounded Replay was designed to remove.
