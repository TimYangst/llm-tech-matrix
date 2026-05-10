# Glossary

> 中文版：[README.zh.md](./README.zh.md)

Short reference entries for the techniques that appear across extracted models. Each
entry explains what the technique is, where it came from, and which models in this
repo use it.

The goal is **not** to replace the original papers — entries are 1-2 paragraphs. The
goal is to make `data/extracted/<slug>.md` readable without the reader needing to know
every acronym, and to support synthesis ("which models use auxiliary-loss-free routing?")
by collecting cross-model adoption in one place.

## How to add an entry

1. Copy [`_template.md`](./_template.md) to `<slug>.md` (kebab-case).
2. Fill it in. Keep it short — link to the canonical paper rather than re-explaining.
3. Add a row to the relevant section below.
4. When extracting a new model that uses the technique, add a row to the entry's
   "Used by" table.

The "Used by" tables are maintained by hand for now. A future synthesis tool can scan
`data/extracted/*.json` for technique mentions and propose additions.

## Index

### Attention

- [Multi-head Latent Attention (MLA)](./mla.md)
- [Grouped Query Attention (GQA)](./gqa.md)
- [QK-Norm](./qk-norm.md)
- [Gated DeltaNet](./gated-deltanet.md)

### FFN / MoE

- [DeepSeekMoE (fine-grained + shared experts)](./deepseekmoe.md)
- [Auxiliary-loss-free routing](./aux-loss-free-routing.md)
- [Global-batch load balancing](./global-batch-load-balancing.md)

### Training objectives

- [Multi-Token Prediction (MTP)](./mtp.md)
- [Fill-in-Middle (FIM)](./fim.md)

### Alignment / RL

- [Group Relative Policy Optimization (GRPO)](./grpo.md)
- [Hybrid Thinking (chat-template thinking-mode fusion)](./hybrid-thinking.md)

### Position embedding / long context

- [YaRN RoPE scaling](./yarn-rope.md)
- [Dual Chunk Attention (DCA)](./dual-chunk-attention.md)
- [Multimodal RoPE (mRoPE)](./mrope.md)

### Quantization / mixed precision

- [FP8 mixed precision (DeepSeek-V3 variant)](./fp8-mixed-precision.md)

### Distributed training

- [DualPipe pipeline scheduling](./dualpipe.md)
