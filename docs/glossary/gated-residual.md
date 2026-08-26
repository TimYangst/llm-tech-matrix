# Gated Residual (GR)

> 中文版：[gated-residual.zh.md](./gated-residual.zh.md)

**Slug:** `gated-residual`
**Category:** other
**One-line:** A widened residual stream (4 parallel branches) read through an elementwise, data-dependent sigmoid gate and written through a per-branch scalar — with the inter-branch mixing matrix of Hyper-Connections dropped entirely.
**First introduced in:** [On the Design of Qwen3.8-Next Architecture (Qwen Team, 2026)](https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf) §2.2

## Description

Pre-normalization keeps deep transformers trainable but attenuates what each layer
receives: every block reads the same stream, so a feature written early competes with
everything written after it. Two families of fix exist — make each layer's *read and write*
more expressive (highway networks), or *widen the stream itself* into several parallel
branches (AltUp, [Hyper-Connections](./mhc.md)). GR's premise is that they are
complementary: widening adds capacity, and a richer read decides how that capacity is spent.

GR keeps `n_r = 4` branches and asks where the added expressiveness actually pays. The
ablation's answer is unusually clean, and it is where GR diverges from HC/mHC:

- **Read granularity matters; write granularity does not.** Refining the read from one
  scalar per branch to one weight per branch *and channel* helps; the same refinement of
  the write "gives almost nothing". So GR's read is elementwise and its write stays a
  per-branch scalar.
- **`H_res` earns nothing.** Once read and write are expressive enough, the `n_r × n_r`
  inter-branch mixing operator — the component HC puts its capacity into, and which mHC
  further constrains to a doubly-stochastic manifold — "brings no significant improvement".
  GR drops it. That removes a full read of the residual state per block (the dominant
  inference cost of a widened stream) and eliminates a constraint-bearing source of
  instability. With no mixing operator the branches stay independent, which also makes the
  information flow tractable to analyse.
- **Bounded positive gates beat tanh**, in both loss and stability — consistent with the
  same finding in the GDN and attention output gates.
- **Read all branches**, normalized separately (a group RMSNorm over the widened stream),
  rather than pooling them or reading only the last.

The read that survives this ablation turned out to be exactly *GatedNorm* — a lightweight
elementwise self-gate after RMSNorm, found in separate work to markedly improve training
stability — applied to the widened stream. Qwen merged the two, which is where the name
comes from. Because the read already normalizes and gates, **GR replaces the block's
pre-normalization** rather than sitting in front of it, so widening adds no norm layer.

The stability consequence is the point of the design, not a side effect. Under a stress
test at 4× the optimal learning rate, the previous-generation structure spikes frequently
while the GR recipe stays stable; isolating the gate on a single-variable pair identifies it
as the key contributor. Qwen reports the full-scale run completing with no loss spike and
**without qk-clip or SwiGLU-clip** — the explicit clipping crutches other vendors rely on.
That stability margin is then *spent*: it is what allows the refitted scaling law to
recommend a higher learning rate and batch size.

## Reference materials

- Original paper: <https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf> (§2.2)
- Hyper-Connections (the family GR belongs to): <https://arxiv.org/abs/2409.19606>
- Reference implementation: — (config keys `hc_count`, `hc_lowrank`)

## Used by

| Model | Variation / details |
| ----- | ------------------- |
| Qwen3.8-Flash-Next | `n_r = 4` branches (`hc_count=4`), low-rank bottleneck of `d/8 = 320` (`hc_lowrank=320`), a **separate GR module for the attention block and the MLP block of every layer**. Read: per-branch RMSNorm with its own gain → elementwise sigmoid gate predicted from all branches → mean of gated branches. Write: `s = 2·σ(W_w vec(R̂))`, one scalar per branch. No static term, no special init. Ablation at 25B-A3B / 560B tokens: pre-norm 1.617 loss / 50.91 avg → mHC static 1.596 / 52.49 → mHC dynamic 1.594 / 54.47 → **GR 1.590 / 54.66**. Residual state supports FP8 storage at inference to contain the memory traffic of 4 branches. |

## Related techniques

- [mHC / Hyper-Connections](./mhc.md) — the same family. HC and mHC keep scalar read/write and spend capacity on `H_res`; GR spends it on the read and deletes `H_res`. At 25B-A3B the two are comparable in quality, and GR wins on efficiency and stability.
- [AttnRes](./attnres.md) — Kimi K3's alternative, which uses softmax attention over earlier layers' outputs to form each sublayer's read. Head-to-head at 28 layers, full AttnRes reaches 1.762 loss and GR (`n_r=4`) matches it at 1.762.
- [Muon](./muon.md) — GR's two low-rank projections are deliberately excluded from Muon and kept on AdamW, because of their very elongated shapes.
