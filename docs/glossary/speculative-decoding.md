# Speculative decoding modules (MTP-1 → EAGLE-3 / DSpark)

> 中文版：[speculative-decoding.zh.md](./speculative-decoding.zh.md)

**Slug:** `speculative-decoding`
**Category:** infra
**One-line:** A small draft model proposes a block of tokens that the full model verifies in one forward pass, accepting the longest prefix consistent with the target distribution — lossless by construction, and by mid-2026 a *shipped weight-bearing module* rather than a serving-side afterthought.
**First introduced in:** Speculative decoding (Chen et al., 2023; Leviathan et al., 2023). The two variants tracked here are [EAGLE-3 (Li et al., 2025)](https://arxiv.org/abs/2503.01840) and [DSpark (DeepSeek-AI, 2026)](https://arxiv.org/abs/2607.05147).

## Description

Autoregressive decoding costs one full forward pass per token. Speculative decoding decouples
*drafting* from *verification*: a lightweight draft proposes γ candidate tokens, the target
model verifies the whole block in a single forward pass via rejection sampling, and the longest
prefix consistent with the target distribution is accepted plus one bonus token. Because
verification is parallel and the acceptance rule preserves the target distribution exactly,
there is **no quality loss** — only a latency win whose size is governed by the acceptance rate.

The design tension is drafting latency vs acceptance rate:

- **Autoregressive drafters** condition each position on the previously sampled one, so
  acceptance is high but drafting latency grows linearly with block size — forcing short blocks
  and shallow architectures.
- **Parallel drafters** emit all positions in one forward pass, making latency nearly
  independent of block size, but they cannot model inter-token dependencies within a block,
  which causes multi-modal collisions and rapid acceptance decay at later positions.

Two 2026 flagship models converged on making the draft a first-class part of the checkpoint,
within weeks of each other — and both did it by **repurposing or replacing the MTP head**:

**EAGLE-3 style (Kimi K3).** An EAGLE-3 draft is a single decoder layer whose structure matches
a backbone block — which is exactly the structure of a pre-trained MTP layer, so K3 fine-tunes
its MTP layer into a draft with the target frozen. The draft input fuses low/mid/high-level
target features (K3 takes the outputs of the 1st, 4th and final [AttnRes](./attnres.md) blocks),
concatenated and projected by a bias-free `W_E3` initialized as `[0 0 I]` so it starts equal to
the high-level feature the MTP layer was pre-trained on. Trained unrolled 7 steps on the
likelihood-based LK loss — the negative log of the acceptance rate itself — rather than a KL
surrogate, because minimizing KL does not maximize acceptance for a capacity-limited draft.

**DSpark (DeepSeek-V4).** A *semi-autoregressive* design that keeps the expensive backbone
parallel and adds a cheap sequential module on top:

- **Parallel backbone** — 3 MoE layers with [mHC](./mhc.md) and sliding-window attention of 128,
  conditioned on the target via DFlash-style KV injection: hidden states from a set of target
  layers are concatenated and projected, `H_ctx = RMSNorm(W_c[H^(l₁);…;H^(l_m)])`, then
  concatenated into every draft layer's keys and values.
- **Markov head** — restores intra-block dependency with a first-order transition bias
  `B(x_{k−1}, ·) = W₁[x_{k−1}]W₂`, low-rank at r = 256 so the sequential loop stays cheap even
  at ~10⁵ vocabulary. (An RNN-head variant accumulating full prefix state gave only marginal
  additional gains, so Markov is the default.)
- **Confidence-scheduled verification** — a head `c_k = σ(wᵀ[h_k; W₁[x_{k−1}]])` predicts the
  *conditional* probability that draft token k survives verification given all preceding ones
  were accepted, supervised by the analytical per-step acceptance rate
  `c*_k = 1 − ½‖p_draft − p_target‖`. A hardware-aware scheduler then verifies the full block
  under light load and only the confident prefix under heavy load — because under
  high concurrency, verifying tokens with high rejection risk occupies batch capacity that could
  serve other requests.

Reported against DeepSeek's own MTP-1 production baseline: 60–85% faster per-user generation for
V4-Flash and 57–78% for V4-Pro at matched aggregate throughput.

## Reference materials

- DSpark paper: <https://arxiv.org/abs/2607.05147> · training repo: DeepSpec
- EAGLE-3 paper: <https://arxiv.org/abs/2503.01840>
- Kimi K3 technical report §4.1.4 (draft-model fine-tuning): <https://arxiv.org/abs/2607.24653>
- Schema note: these modules live in `architecture.auxiliary_modules[]` (v7+), separate from the MTP *objective* in `training.objectives.multi_token_prediction`.

## Used by

| Model                  | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4-Flash-0731 | DSpark ships **inside** the checkpoint — the README states the model "has the same model structure as DeepSeek-V4-Flash-DSpark, i.e. it comes with a speculative decoding module attached", and SGLang docs say not to pass `--speculative-draft-model-path`. Config keys: `dspark_block_size=5` (γ), `dspark_markov_rank=256` (r), `dspark_target_layer_ids=[40,41,42]` (KV-injection source layers), `dspark_noise_token_id=128799`. Enabled by one serving flag: vLLM `--speculative-config '{"method":"dspark",...}'`, SGLang `--speculative-algorithm DSPARK`. `config.compress_ratios` grew 44 → 46 entries, consistent with the draft's 3 uncompressed SWA-128 layers. |
| Kimi K3                | EAGLE-3-style draft fine-tuned from the pre-trained MTP layer, target frozen, unrolled 7 steps, LK (acceptance-rate) loss, under the same MXFP4/MXFP8 QAT configuration as the main model. Input fuses features from the 1st / 4th / final AttnRes blocks. **Not shipped**: `config.num_nextn_predict_layers=0` and no draft weights appear in the HF repo — documented in the paper but withheld from the open weights.                                                                                                                                                                                                                                                      |
| GLM-5                  | Not a dedicated draft module, but the same production concern: GLM-5 pairs FP8 rollouts with MTP for tail-latency reduction during RL (paper §3.6.2). Its 3-step MTP is parameter-shared with the backbone.                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Qwen3.8-Flash-Next     | The MTP module doubles as the draft path, and inherits **GLM-5's index-reuse trick**: QSA top-k indices computed once are reused across speculative-decoding steps, so the draft does not re-run indexer selection per step. Measured free — mean accepted length 4.06 → 4.07 under four-step speculative decoding. Unlike DeepSeek's DSpark or Kimi K3's EAGLE-3 conversion, Qwen keeps MTP *as* MTP rather than converting it into a dedicated draft module.                                                                                                                                                                                                                |

## Related techniques

- [Multi-Token Prediction (MTP)](./mtp.md) — the training objective these modules grow out of. MTP-1 was DeepSeek's production speculative-decoding baseline before DSpark; K3's draft is literally its fine-tuned MTP layer.
- [Manifold-Constrained Hyper-Connections (mHC)](./mhc.md) — DSpark's draft backbone uses it too, so target and draft share residual topology.
- [Attention Residuals (AttnRes)](./attnres.md) — supplies the multi-level features Kimi K3's draft consumes.
