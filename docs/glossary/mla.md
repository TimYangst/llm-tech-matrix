# Multi-head Latent Attention (MLA)

> 中文版：[mla.zh.md](./mla.zh.md)

**Slug:** `mla`
**Category:** attention
**One-line:** A low-rank joint compression of attention keys and values into a small latent vector, dramatically shrinking the KV cache while keeping MHA-like quality.
**First introduced in:** [DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model (DeepSeek-AI, 2024)](https://arxiv.org/abs/2405.04434)

## Description

MLA replaces the standard per-head K/V projections with a single down-projection into
a compressed latent vector `c_t^{KV}` (dimension `kv_lora_rank`, typically much smaller
than `num_heads × head_dim`). At inference time only this latent vector is cached, plus
a small RoPE-carrying key vector — so the per-token KV cache footprint is a small
multiple of `kv_lora_rank` rather than scaling with all heads.

To preserve positional information, MLA splits each head's K/Q dimension into a
non-positional part (`qk_nope_head_dim`) recovered via up-projection from the latent,
and a smaller part (`qk_rope_head_dim`) that carries RoPE and is computed separately.
Queries are similarly compressed (via `q_lora_rank`) to reduce activation memory during
training. The value head dim (`v_head_dim`) is independent of the KV cache size.

The net effect: KV cache shrinks by an order of magnitude versus MHA at comparable
quality, which is what makes long-context inference economical for very large models.

## Reference materials

- Original paper: <https://arxiv.org/abs/2405.04434>
- Used and refined in DeepSeek-V3: <https://arxiv.org/abs/2412.19437>

## Used by

| Model                                    | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3                              | `kv_lora_rank=512`, `q_lora_rank=1536`, `qk_nope_head_dim=128`, `qk_rope_head_dim=64`, `v_head_dim=128`, 128 heads                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Kimi K2 family (K2-Thinking, K2.5, K2.6) | Identical MLA dimensions across all three siblings — `kv_lora_rank=512`, `q_lora_rank=1536`, `qk_nope_head_dim=128`, `qk_rope_head_dim=64`, `v_head_dim=128`, 64 heads (half of DeepSeek-V3's 128). HF config reuses the `DeepseekV3ForCausalLM` class for the K2 backbone, so MLA scaling matches V3 modulo head count.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| GLM-5 / GLM-5.1                          | First non-DeepSeek vendor to ship MLA. Dimensions: `kv_lora_rank=512`, `q_lora_rank=2048` (vs DSV3's 1536), `qk_nope_head_dim=192` (vs DSV3's 128), `qk_rope_head_dim=64`, `v_head_dim=256` (vs DSV3's 128), 64 heads. Paper §2.1 motivates the wider head_dim (256 vs DSV3's 192 total) + halved head count (64 vs DSV3's 128) as a roofline-aware adjustment for non-H800 hardware: keep training FLOPs and parameter count constant while reducing the per-decoding-step dot-product width. **Muon Split** optimizer adaptation (paper §2.1, [Muon](./muon.md)) is what closes the MLA-vs-GQA-8 quality gap and removes the need for QK-Clip — splits the W_UQ/W_UK/W_UV matrices per-head and orthogonalizes each independently. MLA is composed with [DSA (DeepSeek Sparse Attention)](./dsa.md) — DSA sparsifies which compressed-KV entries the core MLA attention reads from. |
| Kimi K3                                  | **Gated MLA** — MLA retained only in the periodic global-attention layers (24 of 93, interleaved 3:1 with KDA), with two changes vs K2/K2.5. (1) **NoPE on all MLA layers** (`mla_use_nope=true`): the interleaved KDA layers supply position-sensitivity, MLA supplies unrestricted global content interaction, and decoupling the two means context extension never has to retune a RoPE base or apply YaRN. (2) An input-dependent channel-wise **full-rank output gate** `y = W_o[σ(W_g x) ⊙ õ]` (`mla_use_output_gate=true`), matching KDA's gate parameterization. Latent dims unchanged from K2: kv_lora_rank=512, q_lora_rank=1536, qk_nope 128 / qk_rope 64, v_head_dim 128; 96 query heads (vs K2's 64). Attention output kept in FP32 during training to correct flash-attention's biased rounding error.                                                                  |
| DeepSeek-V3.2-Exp                        | MLA config byte-identical to DeepSeek-V3 (kv_lora_rank=512, q_lora_rank=1536, qk_nope 128 / qk_rope 64, v_head_dim 128, 128 heads, 61 layers). The change is that [DSA](./dsa.md) is layered on top, which forces MLA into its **MQA mode** throughout — V3.1-Terminus had used the MHA mode for training and prefilling and MQA only for decoding, but DSA needs each latent KV entry shared across all query heads for kernel efficiency.                                                                                                                                                                                                                                                                                                                                                                                                                                           |

## Related techniques

- [GQA (Grouped-Query Attention)](./gqa.md) — _placeholder; predecessor approach to KV cache reduction_
- [YaRN RoPE scaling](./yarn-rope.md) — DeepSeek-V3 applies YaRN exclusively to the decoupled RoPE key in MLA
