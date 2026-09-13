# DeepSeek-V4.1-Flash

Slug: `deepseek-v4.1-flash`
Family: `DeepSeek`
Status: `extracted`

## Sources

Authoritative list in `data/sources/deepseek-v4.1-flash/manifest.json`. All HF assets are
**pinned to revision `dba1be0a40aa45a94ad051997016db3960a90277`** (2026-09-10), not `main`,
after the Qwen3.8-Flash-Next README drifted post-extraction (see that model's notes).

Registered:

- [x] `config` (`hf_config`) — `config.json` (text_config + vision_config split)
- [x] `readme` (`model_card`) — `README.md`
- [x] `tokenizer_config` (`other`) — `tokenizer_config.json`
- [x] `encoding_readme` (`other`) — `encoding/README.md` (wire format; still no Jinja template)
- [x] `inference_readme` (`other`) — `inference/README.md`
- [x] `inference_config` (`other`) — `inference/config.json` (reference-impl key names; confirms `n_mtp_layers=3`)
- [x] `tech_report` (`tech_report`) — `DeepSeek_V41_Tech_Report.pdf` (HF-hosted; the README cites no arXiv ID)
- [x] `api_news` (`blog_html`) — `https://api-docs.deepseek.com/news/news260910/`

Considered but excluded:

- `inference/model.py`, `engram.py`, `vision.py`: code, not documentation. Every config key they
  consume already has a report citation.
- The Engram paper (arXiv:2601.07372) and DSpark paper (arXiv:2607.05147): the V4.1 report
  restates everything the record uses, and DSpark is already registered on `deepseek-v4-flash-0731`.
- Third-party GGUF/FP8 re-quantizations (AMAImedia, vcruz305): not vendor sources.

## Open questions

See `data/extracted/deepseek-v4.1-flash.json` `open_questions`. The ones that matter:

1. **Schema gaps: resolved by schema v8** (same batch).
   - CED and CSA2 are now in `attention.cross_layer_sharing[]`.
   - Engram is now in `memory_modules[]`.
   - The numeric effort axis is now in `alignment.reasoning_effort`.
   - Still open: phase-dependent active parameters (8B prefill / 16B decode), which has only
     one occurrence so far.
2. **Numeric effort still needs a placeholder in `inference_modes[].kwargs`**
   (`<integer 1-100>`). The structured view in `reasoning_effort` is the one to query.
3. **`num_nextn_predict_layers=3` while the report says MTP was omitted.** The key matches
   DSpark's 3 blocks, and `compress_ratios` has exactly 3 trailing entries. If that reading
   holds, it also answers the `deepseek-v4-flash-0731` `compress_ratios` (46 = 43 + 3) question.
4. **The disappearances are inferred only from what the sources don't say.** Hash routing
   (`num_hash_layers` gone), Anticipatory Routing (never mentioned), the `developer` role
   (not in the role list) and FIM (not mentioned) are all absent without explanation.
5. **NL2Repo-Bench is 64.0 in the README but 65.4 in report Table 3.**

## Resolved

- **Is V4.1 a refresh of V4-Flash?** No. It has a new HF class (`DeepseekV41ForCausalLM`) and
  a new layer topology (CED 20+20). V4's CSA/HCA alternation is gone, replaced by pure CSA2.
  Hidden size 4096 → 5120, experts 256 → 384 (width 2304), indexer heads 64 → 32, layers
  43 → 40. The API note calls it "the smallest model in our new architecture family".
- **Why are there two active-parameter numbers?** CED projects decoder global KV from the final
  encoder hidden state. Prefill can stop after the 20-layer encoder (8B active); decoding runs
  all 40 layers (16B).
- **Does V4.1 still train an MTP head?** No. From the report: "We omit the MTP module during
  backbone pre-training and use DSpark". DSpark is trained in a separate stage with the backbone
  frozen, then co-trained during post-training with no gradient flowing into the backbone.
- **Is the post-training algorithm new?** No, and the report says so. It keeps SFT → async GRPO
  RL → OPD and attributes all gains to task and environment synthesis. OPD now uses more
  than 40 teachers.
- **Config ↔ report layer layout reconciles exactly.**
  - `kv_source_layer_ids` [2,8,14,20] are the Full layers.
  - `index_source_layer_ids` are Full ∪ Reindex (adding 24,28,32,36).
  - `compress_ratios` reads [0,0, 2×18, 1×20, 0×3].
  - `candidate_source_layer_id`=20 is the first decoder Full layer.
- **Engram parameter count reconciles.** `engram_num_embeddings` ≈ 384M per module × 256 dims
  ≈ 98.3B, and two modules ≈ 196.6B, which matches the reported 196B.
- **API reasoning tiers.** `low`/`high`/`max` map to 50/75/100 (report Table 2 and the encoding
  README), and the encoder default is now `high`.

## Notes

- **The vendor-convergence story continues, now inside DeepSeek's own line.**
  - Engram gives DeepSeek embedding-table capacity scaling, the same axis Qwen's Flash-Next
    n-gram layer uses. The report notes its layer 1 placement lets prefetch overlap the first
    block, Qwen's exact layer-2 rationale.
  - Head-wise Muon is explicitly credited to GLM-5 and Kimi-K3.
  - CSA2's Reindex/Reuse cites IndexCache (GLM-5.2's IndexShare).
  - The Hierarchical Sparse Indexer attacks the same indexer-cost term as Qwen's QSA.
- **Vision arrives in the DeepSeek main line.** It uses a from-scratch DeepSeek-ViT (32L,
  SigLIP contrastive, then an AR fine-tune through a throwaway 4B MoE). This is the same
  from-scratch choice Kimi K3 made with MoonViT-V2.
- **The KV-cache-per-token lineage is now a headline metric.** Figure 1(b) reports 890 bytes
  per token: ~1/4 of V4-Flash and 1/437 of DeepSeek-V1.
- **Not yet extracted from the same family:**
  - `DeepSeek-V4-Pro-0813` (V4-Pro GA, 2026-08-13).
  - `DeepSeek-V4-Flash-Vision-Exp` (2026-08-21, API-retired by this release).
  - The announced but unreleased V4.1-Pro.
