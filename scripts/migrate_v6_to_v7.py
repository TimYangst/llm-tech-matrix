"""One-shot migration: schema v6 → v7.

For each data/extracted/<slug>.json:
- Bump schema_version to 7.
- Populate the four new v7 slots where the facts are ALREADY present in the record's prose
  (or in its cited sources). This is a restatement into structured form, never new research:
    * architecture.attention.sparse_attention  (DSA / CSA / HCA indexer parameters)
    * architecture.attention.notes             (attention-level details with no other home)
    * architecture.ffn.moe.latent_dim          (LatentMoE routed-expert width)
    * architecture.auxiliary_modules[]         (speculative-decoding drafts)
    * training.quantization                    (shipped-weight precision recipe)

All new fields are optional with defaults, so a v6 record is valid as v7 with a bare
schema_version bump; the per-slug content below is what makes the v7 records carry real data.

Records deliberately left at defaults:
- Qwen3 / Qwen3.5 / Qwen3.6, DeepSeek-V3 — dense attention, no shipped-weight quantization,
  no auxiliary modules.
- DeepSeek-V3.2-Exp ships in its FP8 *training* precision, so training.quantization stays
  None by the field's own definition; the FP8 recipe remains in advanced.mixed_precision.
- MTP heads are recorded as training objectives, not auxiliary_modules, unless the vendor
  ships them as a distinct attached module with its own activation path.

Usage:
    uv run python scripts/migrate_v6_to_v7.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = REPO_ROOT / "data" / "extracted"

UNKNOWN = "[Unknown/Not Disclosed]"

# ---------------------------------------------------------------------------
# Shared content: the DeepSeek-V4 family's quantization recipe is identical across
# Pro / Flash / Flash-0731 (paper §5.2.1), so define it once.
# ---------------------------------------------------------------------------

V4_QUANTIZATION: dict[str, Any] = {
    "weight_format": "mxfp4",
    "activation_format": "fp8-e4m3 (config.quantization_config.activation_scheme='dynamic', scale_fmt='ue8m0')",
    "method": "qat",
    "scope": (
        "MoE expert weights (config.expert_dtype='fp4') plus the Query-Key path of CSA's "
        "lightning indexer, whose QK activations are cached, loaded and multiplied entirely "
        "in FP4 with index scores further quantized FP32→BF16. Non-expert parameters remain "
        "FP8/BF16. KV cache: BF16 for RoPE dimensions, FP8 for the rest."
    ),
    "granularity": "weight_block_size 128x128 FP8 blocks, each absorbing 1x32 FP4 sub-block scales",
    "stage": (
        "Post-training FP4 QAT: FP32 master weights quantized to FP4 then dequantized "
        "losslessly to FP8 for compute, backward via straight-through estimator. Inference "
        "and RL rollout both use native FP4 weights."
    ),
    "notes": "Shipped checkpoint is labelled 'FP4 + FP8 Mixed'.",
}

KIMI_K2_QUANTIZATION: dict[str, Any] = {
    "weight_format": "int4",
    "activation_format": UNKNOWN,
    "method": "qat",
    "scope": (
        "Routed-expert linears only. Excluded via config.quantization_config.ignore: "
        "self_attn, shared_experts, the dense mlp gate/up/down projections, lm_head "
        "(and vision_tower / mm_projector on the multimodal siblings)."
    ),
    "granularity": "compressed-tensors pack-quantized, group_size=32, num_bits=4, type=int, symmetric, strategy=group, observer=minmax",
    "stage": "Post-training QAT; all published benchmark results are reported under INT4 precision.",
    "notes": (
        "Checkpoints can be unpacked to FP8/BF16 via the official compressed-tensors repo "
        "for higher-precision deployment."
    ),
}

# ---------------------------------------------------------------------------
# Per-slug content.
# ---------------------------------------------------------------------------

EDITS: dict[str, dict[str, Any]] = {
    "deepseek-v3.2-exp": {
        "sparse_attention": {
            "kind": "dsa",
            "selection": (
                "Top-k by lightning-indexer score I_{t,s} = sum_j w^I_{t,j} * ReLU(q^I_{t,j} . k^I_s); "
                "core attention runs only over the retained key-value entries."
            ),
            "top_k": 2048,
            "indexer_heads": 64,
            "indexer_head_dim": 128,
            "kv_compression_ratio": UNKNOWN,
            "training_recipe": (
                "Retrofitted onto the dense DeepSeek-V3.1-Terminus checkpoint in two stages. "
                "(1) Dense warm-up: LR 1e-3, 1000 steps x 16 sequences x 128K = 2.1B tokens, "
                "dense attention retained, everything frozen except the indexer, which is "
                "trained by KL against the model's own head-summed L1-normalized attention "
                "distribution. (2) Sparse adaptation: LR 7.3e-6, 15000 steps x 480 sequences "
                "x 128K = 943.7B tokens, top-k selection on, all parameters trainable, the "
                "same KL loss restricted to the selected token set. The indexer input is "
                "detached from the computational graph throughout, so the indexer is driven "
                "only by L_I and the main model only by the language-modeling loss."
            ),
            "notes": (
                "The canonical DSA reference implementation. Instantiated under MLA in MQA mode "
                "because kernel efficiency requires each KV entry to be shared across query heads "
                "(V3.1-Terminus used MLA's MHA mode for training/prefill and MQA only for decode). "
                "Core attention drops from O(L^2) to O(Lk); the indexer itself remains O(L^2) but "
                "is cheap — few heads, ReLU for throughput, implementable in FP8. A masked-MHA "
                "mode simulates DSA for short-sequence prefilling."
            ),
        },
    },
    "deepseek-v4-pro": {
        "sparse_attention": {
            "kind": "csa+hca",
            "selection": (
                "CSA layers: top-k by lightning indexer over COMPRESSED entries (the V3.2-Exp "
                "indexer mechanism applied after compression). HCA layers: no selection — dense "
                "attention over heavily compressed entries."
            ),
            "top_k": 1024,
            "indexer_heads": 64,
            "indexer_head_dim": 128,
            "kv_compression_ratio": "4 (CSA, two interleaved softmax-weighted compressors over overlapping windows) / 128 (HCA, non-overlapping)",
            "training_recipe": (
                "Trained in from the start rather than retrofitted, on a curriculum: the first "
                "1T tokens use dense attention, then sparse attention is introduced at the 64K "
                "sequence-length stage after a short Lightning-Indexer warm-up pass."
            ),
            "notes": (
                "Extends DSA by adding token-level KV compression before selection. Each layer "
                "also carries a supplementary uncompressed sliding-window branch (n_win=128) and "
                "a per-head learnable attention sink. See attention.layer_pattern for the "
                "CSA/HCA interleave."
            ),
        },
        "quantization": V4_QUANTIZATION,
    },
    "deepseek-v4-flash": {
        "sparse_attention": {
            "kind": "csa+hca",
            "selection": (
                "CSA layers: top-k by lightning indexer over COMPRESSED entries. HCA layers: no "
                "selection — dense attention over heavily compressed entries."
            ),
            "top_k": 512,
            "indexer_heads": 64,
            "indexer_head_dim": 128,
            "kv_compression_ratio": "4 (CSA) / 128 (HCA)",
            "training_recipe": (
                "First 1T tokens dense; sparse attention introduced at the 64K sequence-length "
                "stage after a short Lightning-Indexer warm-up pass."
            ),
            "notes": (
                "Same mechanism as V4-Pro at a smaller selection budget (top-k 512 vs 1024). "
                "Layers 0-1 are pure SWA rather than sparse — the Flash-specific deviation from "
                "Pro, which uses pure HCA there."
            ),
        },
        "quantization": V4_QUANTIZATION,
    },
    "deepseek-v4-flash-0731": {
        "sparse_attention": {
            "kind": "csa+hca",
            "selection": (
                "CSA layers: top-k by lightning indexer over COMPRESSED entries. HCA layers: no "
                "selection — dense attention over heavily compressed entries."
            ),
            "top_k": 512,
            "indexer_heads": 64,
            "indexer_head_dim": 128,
            "kv_compression_ratio": "4 (CSA) / 128 (HCA)",
            "training_recipe": (
                "Unchanged from the preview — no re-pre-training occurred. First 1T tokens "
                "dense; sparse attention introduced at the 64K sequence-length stage."
            ),
            "notes": (
                "Byte-identical indexer configuration to the preview (index_n_heads=64, "
                "index_head_dim=128, index_topk=512). Serving enables an FP4 indexer cache "
                "(vLLM `--attention-config '{\"use_fp4_indexer_cache\": true}'`)."
            ),
        },
        "quantization": V4_QUANTIZATION,
        "auxiliary_modules": [
            {
                "name": "DSpark speculative-decoding module",
                "purpose": "speculative_decoding",
                "architecture": (
                    "Semi-autoregressive draft. Parallel backbone: 3 MoE layers with mHC and "
                    "sliding-window attention of 128, conditioned on the target via DFlash-style "
                    "KV injection — hidden states from target layers [40, 41, 42] "
                    "(config.dspark_target_layer_ids) concatenated and projected as "
                    "H_ctx = RMSNorm(W_c[H^(l1);...;H^(lm)]), then concatenated into every draft "
                    "layer's keys and values. Shares the target's frozen embedding and LM head. "
                    "Sequential module: a Markov head adding a first-order transition bias "
                    "B(x_{k-1}, .) = W1[x_{k-1}]W2 at rank 256 (config.dspark_markov_rank), which "
                    "restores intra-block dependency and mitigates the suffix acceptance decay of "
                    "purely parallel drafters. Confidence head: c_k = sigmoid(w^T[h_k; W1[x_{k-1}]]) "
                    "predicting per-position survival probability. Max block size gamma=5 "
                    "(config.dspark_block_size)."
                ),
                "shipped_in_checkpoint": True,
                "activation": (
                    "vLLM: --speculative-config '{\"method\":\"dspark\",\"num_speculative_tokens\":7,"
                    "\"draft_sample_method\":\"greedy\"}'. SGLang: --speculative-algorithm DSPARK with "
                    "NO --speculative-draft-model-path, since target and draft weights come from the "
                    "same checkpoint."
                ),
                "notes": (
                    "Supersedes MTP-1 as DeepSeek's production speculative-decoding baseline: "
                    "60-85% faster per-user generation at matched throughput for V4-Flash "
                    "(arXiv:2607.05147). Verification is confidence-scheduled — a hardware-aware "
                    "prefix scheduler verifies the full block under light load and only the "
                    "confident prefix under heavy load, so batch capacity is not spent on tokens "
                    "with high rejection risk. Published speedups were measured with drafts "
                    "co-deployed against the PREVIEW targets, not this checkpoint."
                ),
            }
        ],
    },
    "glm-5": {
        "sparse_attention": {
            "kind": "dsa",
            "selection": "Top-k by lightning-indexer score, per the DeepSeek-V3.2-Exp mechanism.",
            "top_k": 2048,
            "indexer_heads": 32,
            "indexer_head_dim": 128,
            "kv_compression_ratio": UNKNOWN,
            "training_recipe": (
                "Continued Pre-Training (paper §2.1.1): indexer-only warm-up for 1000 steps x 14 "
                "sequences x 202752 tokens at max LR 5e-3 (~2.84B tokens), then sparse adaptation "
                "on 20B tokens — two orders of magnitude cheaper than DeepSeek-V3.2-Exp's 943.7B "
                "and still sufficient to recover dense-baseline quality."
            ),
            "notes": (
                "First non-DeepSeek adoption of DSA. config.indexer_rope_interleave=true. "
                "Paper §2.1.2 ablates DSA against SWA, search-based-pattern SWA, GDN and "
                "SimpleGDN and concludes DSA is the only one lossless by construction, since the "
                "indexer adapts to content instead of committing to a fixed sparsity pattern. "
                "RL-stability requirement (§3.2): the top-k operator must be deterministic — "
                "non-deterministic CUDA top-k caused sharp entropy collapse within a few steps, "
                "so GLM-5 uses torch.topk and freezes indexer parameters during RL by default."
            ),
        },
        "quantization": {
            "weight_format": "int4",
            "activation_format": UNKNOWN,
            "method": "qat",
            "scope": UNKNOWN,
            "granularity": UNKNOWN,
            "stage": (
                "QAT applied during SFT (paper §2.4.3), with a quantization kernel that "
                "guarantees bitwise-identical behaviour between training and inference and is "
                "used both at training time and for offline weight quantization."
            ),
            "notes": (
                "A separate GLM-5-FP8 deployment sibling is POST-training quantized for "
                "single-node deployment — a different recipe from this INT4 QAT path."
            ),
        },
    },
    "glm-5.1": {
        "sparse_attention": {
            "kind": "dsa",
            "selection": "Top-k by lightning-indexer score, per the DeepSeek-V3.2-Exp mechanism.",
            "top_k": 2048,
            "indexer_heads": 32,
            "indexer_head_dim": 128,
            "kv_compression_ratio": UNKNOWN,
            "training_recipe": (
                "Inherited from GLM-5 — a post-training-only refresh, so the indexer weights and "
                "the Continued Pre-Training recipe carry over unchanged."
            ),
            "notes": (
                "Config byte-identical to GLM-5 except transformers_version. Same deterministic "
                "top-k requirement and indexer-frozen-during-RL discipline."
            ),
        },
        "quantization": {
            "weight_format": "int4",
            "activation_format": UNKNOWN,
            "method": "qat",
            "scope": UNKNOWN,
            "granularity": UNKNOWN,
            "stage": "INT4 QAT during SFT, inherited from GLM-5.",
            "notes": "A GLM-5.1-FP8 deployment sibling is post-training quantized, mirroring the GLM-5/GLM-5-FP8 pair.",
        },
    },
    "kimi-k2-thinking": {"quantization": KIMI_K2_QUANTIZATION},
    "kimi-k2.5": {"quantization": KIMI_K2_QUANTIZATION},
    "kimi-k2.6": {"quantization": KIMI_K2_QUANTIZATION},
    "kimi-k3": {
        "moe_latent_dim": 3584,
        "attention_notes": (
            "Three attention-level choices that cut across both variants. (1) NoPE everywhere — "
            "config.mla_use_nope=true; position is carried implicitly by KDA's channel-wise decay "
            "recurrence, which is what lets the model extrapolate to 1M tokens with no RoPE "
            "rescaling or YaRN. (2) Full-rank input-dependent output gates on BOTH variants — "
            "y = W_o[Sigmoid(W_g x) * o~] (config.mla_use_output_gate=true, "
            "config.linear_attn_config.use_full_rank_gate=true), replacing Kimi Linear's low-rank "
            "gate. (3) The MLA attention output is kept in FP32 during training to correct flash "
            "attention's biased rounding error, with the training kernel redesigned to overlap the "
            "doubled on-chip output tile with the KV staging buffers."
        ),
        "quantization": {
            "weight_format": "mxfp4",
            "activation_format": "mxfp8",
            "method": "qat",
            "scope": (
                "MoE expert weights only. config.quantization_config.ignore excludes self_attn, "
                "shared_experts, the dense mlp gate/up/down projections, lm_head, vision_tower "
                "and mm_projector; latent-MoE projections and routers also stay in higher precision."
            ),
            "granularity": "compressed-tensors 'mxfp4-pack-quantized', num_bits=4, type=float, group_size=32, symmetric, strategy=group, observer=minmax",
            "stage": (
                "QAT from the SFT stage onward through all of RL. During RL, rollout and training "
                "share the same quantization scheme, eliminating the train-inference mismatch."
            ),
            "notes": (
                "A format shift for the vendor: the K2 family (K2-Thinking / K2.5 / K2.6) shipped "
                "native INT4, K3 moves to MXFP4 weights + MXFP8 activations 'for broad hardware "
                "compatibility' — the same MX format family DeepSeek-V4 uses for its expert weights."
            ),
        },
        "auxiliary_modules": [
            {
                "name": "EAGLE-3 draft model (fine-tuned from the pre-trained MTP layer)",
                "purpose": "speculative_decoding",
                "architecture": (
                    "A single decoder layer mirroring a backbone block — the same shape as an "
                    "EAGLE-3 draft, which is why the pre-trained MTP layer could be fine-tuned "
                    "into one directly. Its input fuses low/mid/high-level target features taken "
                    "from the outputs of the 1st, 4th and final AttnRes blocks, concatenated and "
                    "projected by a bias-free W_E3 initialized as [0 0 I] so that at "
                    "initialization the fused representation equals the high-level feature the "
                    "MTP layer was pre-trained on."
                ),
                "shipped_in_checkpoint": False,
                "activation": "",
                "notes": (
                    "Trained with the target frozen, unrolled 7 steps (EAGLE-3 training-time test "
                    "protocol), optimizing the likelihood-based LK loss — the negative log of the "
                    "speculative-sampling acceptance rate — rather than a KL surrogate, at "
                    "temperature 1 with no auxiliary ground-truth cross-entropy term. Follows the "
                    "same MXFP4/MXFP8 QAT configuration as the main model. NOT in the released "
                    "checkpoint: config.num_nextn_predict_layers=0 and no draft weights appear in "
                    "the HF repo, so this records a module the paper documents but the open "
                    "weights withhold."
                ),
            }
        ],
    },
}


def migrate(path: Path) -> bool:
    """Migrate one extracted record in place. Returns True if the file changed."""
    original = path.read_text(encoding="utf-8")
    record = json.loads(original)
    slug = path.stem

    record["schema_version"] = 7

    edits = EDITS.get(slug, {})
    if "sparse_attention" in edits:
        record["architecture"]["attention"]["sparse_attention"] = edits["sparse_attention"]
    if "attention_notes" in edits:
        record["architecture"]["attention"]["notes"] = edits["attention_notes"]
    if "moe_latent_dim" in edits:
        record["architecture"]["ffn"]["moe"]["latent_dim"] = edits["moe_latent_dim"]
    if "auxiliary_modules" in edits:
        record["architecture"]["auxiliary_modules"] = edits["auxiliary_modules"]
    if "quantization" in edits:
        record["training"]["quantization"] = edits["quantization"]

    updated = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    paths = sorted(EXTRACTED_DIR.glob("*.json"))
    if not paths:
        print(f"No extracted records found in {EXTRACTED_DIR}", file=sys.stderr)
        return 1

    unknown_slugs = set(EDITS) - {p.stem for p in paths}
    if unknown_slugs:
        print(f"EDITS references unknown slugs: {sorted(unknown_slugs)}", file=sys.stderr)
        return 1

    changed = 0
    for path in paths:
        if migrate(path):
            changed += 1
            print(f"  migrated  {path.relative_to(REPO_ROOT)}")
        else:
            print(f"  unchanged {path.relative_to(REPO_ROOT)}")
    print(f"Done. {changed}/{len(paths)} record(s) rewritten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
