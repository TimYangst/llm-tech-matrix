# Kimi K3

Slug: `kimi-k3`
Family: `kimi-k3`
Status: `extracted`

## Sources

Authoritative list in `data/sources/kimi-k3/manifest.json`.

Registered:

- [x] `config` (`hf_config`) — `https://huggingface.co/moonshotai/Kimi-K3/raw/main/config.json`
- [x] `readme` (`model_card`) — `https://huggingface.co/moonshotai/Kimi-K3/raw/main/README.md`
- [x] `generation_config` (`other`) — `https://huggingface.co/moonshotai/Kimi-K3/raw/main/generation_config.json`
- [x] `paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2607.24653` (Kimi K3: Open Frontier Intelligence)
- [x] `blog` (`blog_html`) — `https://www.kimi.com/blog/kimi-k3`

Not available: the HF repo publishes no `tokenizer_config.json` and no `chat_template.jinja` — the
XTML template lives inside the vendor's `encoding_k3.py`. Tool-call wire format was therefore
extracted from paper §F + Fig. 16 rather than from a machine-readable template.

## Open questions

- [ ] **Total pre-training tokens** — not disclosed. The paper retunes tokens-per-parameter by scaling law (§3.2) but reports neither the TPP nor the absolute budget. First Kimi extraction missing this.
- [ ] **MTP layer count** — paper Table 1 and §4.1.4 say 1 MTP layer was pre-trained; released `config.json` has `num_nextn_predict_layers=0`. Reading: repurposed into an EAGLE-3 draft model for the vendor's serving stack, not shipped in the open checkpoint.
- [ ] **Instruct (non-thinking) mode** — paper §F describes an instruct generation prefix (`[open]response[sep]`), README §6 says thinking is always on. Reachability in self-hosted deployments undocumented.
- [ ] **Reasoning effort `medium`** — the XTML schema reserves four levels (low/medium/high/max); K3 documents only three. Behaviour on `medium` unstated.
- [ ] **Agent Swarm** — K2.5/K2.6's PARL swarm is cited only as prior work (§1) and as a benchmark capability (Swarm Bench, §6.2.1). Whether the swarm serving mode survives into K3 is not stated.
- [ ] **AttnRes block arithmetic** — `attn_res_block_size=12` over 93 layers = 7 full blocks + a 9-layer partial. Paper says "8 blocks with 12-layer size, giving a partial final block and 9 total blocks when counting the embedding layer". Consistent only if the partial counts as the 8th.

### Schema gaps surfaced (drivers for v7)

- [ ] **LatentMoE latent width** — `routed_expert_hidden_size=3584` (0.5× model width) is the defining LatentMoE parameter and has no field; it survives only as prose in `ffn.moe.routing`. Candidate `MoEConfig.latent_dim`.
- [ ] **Quantization is still free text** — K3 is the 7th record with a distinct recipe (MXFP4 weights + MXFP8 activations, QAT from SFT through RL, expert-weights-only) stuffed into `advanced.mixed_precision`. It is also the *second* MXFP4 model after DeepSeek-V4 Pro/Flash — the exact trigger the conventions changelog set for a structured `QuantizationConfig`.

## Resolved

- **Release date** — 2026-07. Blog: "The full model weights will be released by July 27, 2026"; arXiv ID 2607.24653 confirms a July 2026 report.
- **Hybrid attention layout** — 3 KDA : 1 Gated MLA per block over layers 1–92, plus one extra Gated MLA at layer 93 so the final layer is always global. 69 KDA + 24 Gated MLA, explicit in `config.linear_attn_config.{kda_layers,full_attn_layers}` and README §2.
- **NoPE, not YaRN** — `mla_use_nope=true`; paper §2.1.2/§3.4: no positional encoding on any MLA layer, position carried implicitly by KDA's decay recurrence, so 1M extrapolation needs no RoPE rescaling or interpolation. First repo record with `rope.type = "none"`.
- **KDA deltas vs Kimi Linear** — (1) lower-bounded log-decay `g = g_min·Sigmoid(e^A z)`, `g_min = -5` (`gate_lower_bound=-5.0`), which keeps the reciprocal chunk rescaling inside BF16 range and lets *all* causal tiles use dense Tensor Core matmuls (eliminating the position-pair diagonal path); (2) full-rank input-dependent output gate (`use_full_rank_gate=true`).
- **Stable LatentMoE** — 896 routed (16 active, sparsity 56) + 2 full-width shared. Routed experts run in a 3584-wide latent space. Three stabilizers: RMSNorm before `W_up` (`latent_moe_use_norm=true`), SiTU-GLU soft caps, and Quantile Balancing.
- **Quantile Balancing** — replaces the fixed-step aux-loss-free bias update. Bias set from the router-score quantile matching target load `q = mk/n`; Top-(k+1) routing supplies each token's cutoff for free; the global-batch quantile is estimated from a per-expert histogram reduced by one all-reduce of bin counts. Bias affects dispatch only, applies next step, frozen at inference.
- **SiTU-GLU** — `hidden_act='situ'`, β1 = 4 (gate), β2 = 25 (up), output bound 100. Replaces K2's SwiGLU; exists because the 4-matmul-deep routed branch explodes at 2.8T scale in low precision.
- **AttnRes** — Block variant ships: 12-layer blocks, learnable per-layer pseudo-query, RMSNorm'd keys, softmax over block representations (embedding always source 0). Drops memory/PP-communication from O(Ld) to O(Nd).
- **Per-Head Muon** — Newton–Schulz orthogonalization applied per attention head block rather than to the full Q/K/V matrices; equalizes update scale across heads and is slightly cheaper. Weight clipping from K2 retained.
- **MXFP4 QAT, not INT4** — the K2 family's native INT4 QAT is replaced by MXFP4 weights + MXFP8 activations, QAT from SFT through RL with rollout and training sharing the quantization scheme (no train–inference mismatch). Same MX format family as DeepSeek-V4's expert-weight FP4.
- **MoonViT-V2 trained from scratch** — a deliberate break from K2.5's SigLIP-initialized MoonViT-3D, motivated by training stability (SigLIP init shows persistently higher vision-tower gradient norms with spikes). Matches the SigLIP baseline on vision evals.
- **Variant policy** — single unified checkpoint, no thinking toggle, effort via top-level `reasoning_effort`. Nine domain×effort RL experts are consolidated back into one model by MOPD rather than shipped as siblings — the inverse of K2's sibling-per-mode policy.
- **Preserved thinking is mandatory** — not an opt-in third mode as in K2.6 / Qwen3.6. The complete assistant message (including `reasoning_content` and `tool_calls`) must be passed back verbatim.

## Notes

- K3 is a **full architecture rewrite** relative to K2/K2.5/K2.6, not a refresh: every load-bearing component changed (MLA → hybrid KDA+Gated MLA, SwiGLU → SiTU-GLU, DeepSeekMoE → Stable LatentMoE, standard residual → AttnRes, Muon → Per-Head Muon, INT4 → MXFP4, SigLIP-init → from-scratch ViT, RoPE/YaRN → NoPE). The only invariants are hidden dim 7168, vocab 160K, and 1 dense layer.
- Reported ≈2.5× improvement in scaling efficiency over K2 (paper §3.2, Fig. 7), attributed jointly to architecture, data and training-recipe changes.
- First repo record with: linear attention in a *flagship* MoE (`rope.type="none"`), depth-wise attention over layers (AttnRes), latent-space routed experts, quantile-based load balancing, per-head Muon, and an XTML/channel-based chat template.
- Cross-vendor echoes worth tracking in synthesis: MXFP4 expert weights (DeepSeek-V4), On-Policy Distillation (DeepSeek-V4, single-teacher → K3 multi-teacher on two axes), hybrid linear+global attention (Qwen3.5/3.6 Gated DeltaNet at 3:1 — the *same* ratio), aux-loss-free routing (DeepSeek-V3 lineage, now with a quantile update rule).
