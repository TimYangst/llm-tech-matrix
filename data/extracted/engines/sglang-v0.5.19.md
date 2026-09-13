# SGLang v0.5.19

> 中文版：[sglang-v0.5.19.zh.md](./sglang-v0.5.19.zh.md)

*Engine schema version: 2*

## Overview

| Field | Value |
|---|---|
| Repository | https://github.com/sgl-project/sglang |
| License | Apache-2.0 |
| Release tag | `v0.5.19` |
| Commit | `0bcd822377da7b5718e674eaf9c870d349424dd1` |
| Release date | 2026-09-05 |
| Snapshot date | 2026-09-12 |
| Roles | `inference` |
| Hardware | NVIDIA, AMD ROCm, Intel XPU, Intel AMX (CPU), Ascend NPU, Apple Silicon (MLX) |

## Parallelism

| Dimension | Supported | Implementation | Notes | Evidence |
|---|---|---|---|---|
| Tensor | ✓ | tp_size (--tensor-parallel-size) | — | [server_args.py#L940](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L940) |
| Pipeline | ✓ | pp_size (--pipeline-parallel-size); async communication and dynamic chunking | — | [server_args.py#L956](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L956), [pipeline_parallelism.mdx#L12](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/pipeline_parallelism.mdx#L12) |
| Data | ✓ | dp_size (--data-parallel-size); enable_dp_attention (data parallelism for attention, tensor parallelism for FFN); moe_dp_size | The enable_dp_attention help text says the dp size should equal the tp size. | [server_args.py#L972](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L972), [server_args.py#L1078](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L1078) |
| Expert | ✓ | ep_size (--expert-parallel-size / --ep); moe_a2a_backend selects the all-to-all backend (deepep, mooncake, nixl, mori, ...) | The EP guide states DeepEP, Mooncake, NIXL-EP, ascend_fuseep, pplx and MORI only support ep_size = tp_size. v0.5.19 adds a DeepEP v2 ElasticBuffer backend (--moe-a2a-backend deepep_v2) for DeepSeek-V3/V4 and Qwen3-MoE in FP8. | [server_args.py#L2360](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L2360), [expert_parallelism.mdx#L75](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/expert_parallelism.mdx#L75), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| Context | ✓ | dcp_size (--decode-context-parallel-size): stripes the MLA KV cache by token position across a TP group; attn_cp_size (--attention-context-parallel-size) | v0.5.19 runs DCP on the default Blackwell MLA backend trtllm_mla. | [server_args.py#L948](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L948), [server_args.py#L994](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L994), [dcp.mdx#L7](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/dcp.mdx#L7), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| Sequence | ✓ | enable_layernorm_sp (--enable-layernorm-sp) | Megatron-style sequence parallelism for LayerNorm/residual regions under pure tensor parallelism; the help text scopes it to prefill only, Qwen3 dense, tp_size > 1 and NVLink/NVSwitch. New in v0.5.19. | [server_args.py#L1129](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L1129), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |

## Serving

**KV cache management:** RadixAttention's radix tree organizes KV cache by consecutive token spans; HiCache extends it to a HiRadixTree across L1/L2/L3 tiers (GPU, host memory, external storage) with prefetch and write-back policies. v0.5.19 makes the unified radix tree the cache for every model, not just hybrid ones (listed as a breaking change). HiSparse offloads DSA-model KV to host memory.

_Evidence:_ [hicache_design.mdx#L69](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/hicache_design.mdx#L69), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19), [hisparse_guide.mdx#L9](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/hisparse_guide.mdx#L9)

**Prefix caching:** Radix-tree prefix caching (RadixAttention): KV cache of shared prefixes is reused through the radix tree; eviction policies lru, lfu, slru and priority.

_Evidence:_ [hicache_design.mdx#L69](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/hicache_design.mdx#L69), [server_args.py#L327](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L327)

**Disaggregation:** PD disaggregation separates prefill and decode with Mooncake or NIXL as transfer engines (transfer backend choices also include ascend, mori, mooncake_tcp and fake). EPD disaggregation further separates the vision encoder stage for VLMs.

_Evidence:_ [pd_disaggregation.mdx#L21](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/pd_disaggregation.mdx#L21), [server_args.py#L253](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L253), [epd_disaggregation.mdx#L13](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/epd_disaggregation.mdx#L13)

**API surfaces** (3): OpenAI-compatible HTTP API (chat completions), Rust server, Offline Python Engine API (sgl.Engine)

_Evidence:_ [tool_parser.mdx#L100](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/tool_parser.mdx#L100), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19), [tool_parser.mdx#L406](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/tool_parser.mdx#L406)

**Speculative decoding methods** (7): `dflash`, `dspark`, `eagle`, `eagle3`, `frozen_kv_mtp`, `standalone`, `ngram`

_Evidence:_ [spec_info.py#L32](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/speculative/spec_info.py#L32)

**Quantization methods** (32): `awq`, `fp8`, `mxfp8`, `gptq`, `marlin`, `gptq_marlin`, `awq_marlin`, `bitsandbytes`, `gguf`, `modelopt`, `modelopt_fp8`, `modelopt_fp4`, `nvfp4_online`, `modelopt_mixed`, `petit_nvfp4`, `w8a8_int8`, `w8a8_fp8`, `moe_wna16`, `w4afp8`, `mxfp4`, `auto-round`, `auto-round-int8`, `compressed-tensors`, `modelslim`, `mxfp_w4a8`, `quark`, `quark_int4fp8_moe`, `quark_mxfp4`, `mlx_q4`, `mlx_q8`, `unquant`, `humming`

_Evidence:_ [server_args.py#L130](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L130)

**KV cache dtypes** (9): `auto`, `fp8_e5m2`, `fp8_e4m3`, `mxfp8`, `bf16`, `bfloat16`, `nvfp4`, `fp4_mx_block16`, `fp4_e2m1`

_Evidence:_ [server_args.py#L592](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L592)

**Attention backends** (33): `triton`, `torch_native`, `flex_attention`, `dsa`, `nsa`, `dsv4`, `compressed`, `cutlass_mla`, `fa3`, `fa4`, `flashinfer`, `flashmla`, `trtllm_mla`, `cutedsl_mla`, `tokenspeed_mla`, `trtllm_mha`, `dual_chunk_flash_attn`, `hpc_ops`, `minicpm_flashattn`, `minicpm_flashinfer`, `aiter`, `wave`, `intel_amx`, `ascend`, `intel_xpu`, `linear:triton`, `linear:cutedsl`, `linear:flashinfer`, `linear:flashkda`, `linear:nvidia_kda`, `linear:ptx_kda`, `linear:helion`, `linear:intel_xpu`

_Evidence:_ [server_args.py#L171](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L171), [server_args.py#L337](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L337)

**Reasoning parsers** (28): `apertus2509`, `deepseek-r1`, `deepseek-v3`, `deepseek-v4`, `dots`, `glm45`, `ling3`, `hunyuan`, `gpt-oss`, `kimi`, `kimi_k2`, `kimi_k3`, `mimo`, `muse`, `poolside_v1`, `qwen3`, `qwen3-thinking`, `minimax`, `minimax-append-think`, `minimax-m3`, `step3`, `step3p5`, `mistral`, `nemotron_3`, `interns1`, `gemma4`, `inkling`, `cohere_command4`

_Evidence:_ [reasoning_parser.py#L1935](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/parser/reasoning_parser.py#L1935)

**Tool-call parsers** (37): `apertus2509`, `cohere_command4`, `deepseekv3`, `deepseekv31`, `deepseekv32`, `deepseekv4`, `dots`, `glm`, `glm45`, `glm47`, `gpt-oss`, `kimi_k2`, `kimi_k3`, `lfm2`, `ling3`, `llama3`, `mimo`, `minicpm5`, `mistral`, `muse`, `poolside_v1`, `pythonic`, `qwen`, `qwen25`, `qwen3_coder`, `spark25`, `step3`, `step3p5`, `minimax-m2`, `minimax-m3`, `trinity`, `interns1`, `hermes`, `hunyuan`, `gigachat3`, `gemma4`, `inkling`

_Evidence:_ [function_call_parser.py#L73](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/function_call/function_call_parser.py#L73)

_Notes:_ List fields are parsed from the pinned code: SpeculativeAlgorithm enum members (NONE omitted), QUANTIZATION_CHOICES, ATTENTION_BACKEND_CHOICES plus LINEAR_ATTN_KERNEL_BACKEND_CHOICES (prefixed 'linear:'), the kv_cache_dtype choices, reasoning_parser.DetectorMap and FunctionCallParser.ToolCallParserEnum. ATTENTION_BACKEND_CHOICES contains deprecated aliases ('nsa' for 'dsa', 'compressed' for 'dsv4'). No scheduler design doc is among this snapshot's sources, so `scheduler` stays unknown. RL-facing serving features documented in sglang_for_rl.mdx (engine sleep/wake, weight refit, partial rollout) have no v2 field.

## Integrations

| Name | Relation | Notes | Evidence |
|---|---|---|---|
| FlashInfer | `kernel_library` | flashinfer attention backend; FlashInfer moves to 0.6.18 in v0.5.19. | [server_args.py#L184](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L184), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| FlashMLA | `kernel_library` | flashmla attention backend. | [server_args.py#L185](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L185) |
| DeepEP | `kernel_library` | All-to-all communication backend for MoE expert parallelism; DeepEP v2 ElasticBuffer added in v0.5.19. | [expert_parallelism.mdx#L37](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/expert_parallelism.mdx#L37), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| Mooncake | `kv_transfer` | PD disaggregation transfer engine; also an MoE all-to-all backend. | [pd_disaggregation.mdx#L21](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/pd_disaggregation.mdx#L21) |
| NIXL | `kv_transfer` | PD disaggregation transfer engine; also an MoE all-to-all backend. | [pd_disaggregation.mdx#L21](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/pd_disaggregation.mdx#L21) |

## Model support

| Architecture | Model records | Native registry | Documented | Features | Spec. decoding | Evidence |
|---|---|---|---|---|---|---|
| `DeepseekV3ForCausalLM` | [`deepseek-v3`](../deepseek-v3.md), [`kimi-k2-thinking`](../kimi-k2-thinking.md) | ✓ | ✓ | — | `mtp` | [deepseek_v2.py#L3299](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v2.py#L3299), [generative_models.mdx#L42](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/supported-models/generative_models.mdx#L42), [generative_models.mdx#L47](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/supported-models/generative_models.mdx#L47), [model_config.py#L665](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L665) |
| `DeepseekV32ForCausalLM` | [`deepseek-v3.2-exp`](../deepseek-v3.2-exp.md) | ✓ | ✗ | — | `mtp` | [deepseek_v2.py#L3271](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v2.py#L3271), [generative_models.mdx#L42](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/supported-models/generative_models.mdx#L42), [model_config.py#L127](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L127) |
| `DeepseekV4ForCausalLM` | [`deepseek-v4-pro`](../deepseek-v4-pro.md), [`deepseek-v4-flash`](../deepseek-v4-flash.md), [`deepseek-v4-flash-0731`](../deepseek-v4-flash-0731.md) | ✓ | ✗ | — | `mtp`, `dspark` | [deepseek_v4.py#L3932](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v4.py#L3932), [deepseek_v4_dspark.py#L1100](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v4_dspark.py#L1100), [deepseek_v4_nextn.py#L300](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v4_nextn.py#L300), [model_config.py#L678](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L678), [dspark_config.py#L164](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/speculative/dspark_components/dspark_config.py#L164) |
| `DeepseekV41ForCausalLM` | [`deepseek-v4.1-flash`](../deepseek-v4.1-flash.md) | ✗ | ✗ | — | — | [registry.py](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/registry.py), [models](https://github.com/sgl-project/sglang/tree/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models) |
| `Glm4MoeForCausalLM` | [`glm-4.7`](../glm-4.7.md) | ✓ | ✗ | — | `mtp` | [glm4_moe.py#L1516](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/glm4_moe.py#L1516), [tool_parser.mdx#L47](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/tool_parser.mdx#L47), [model_config.py#L693](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L693) |
| `GlmMoeDsaForCausalLM` | [`glm-5`](../glm-5.md), [`glm-5.1`](../glm-5.1.md), [`glm-5.2`](../glm-5.2.md) | ✓ | ✗ | — | `mtp` | [glm4_moe.py#L1444](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/glm4_moe.py#L1444), [model_config.py#L668](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L668), [hisparse_guide.mdx#L123](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/hisparse_guide.mdx#L123), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| `Glm5NextForConditionalGeneration` | [`glm-5.3-flash`](../glm-5.3-flash.md) | ✗ | ✗ | — | — | [registry.py](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/registry.py), [models](https://github.com/sgl-project/sglang/tree/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| `KimiK25ForConditionalGeneration` | [`kimi-k2.5`](../kimi-k2.5.md), [`kimi-k2.6`](../kimi-k2.6.md) | ✓ | ✗ | — | `eagle3` | [kimi_k25.py#L986](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/kimi_k25.py#L986), [kimi_k25_eagle3.py#L1](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/kimi_k25_eagle3.py#L1) |
| `KimiK3ForConditionalGeneration` | [`kimi-k3`](../kimi-k3.md) | ✓ | ✗ | — | `dspark` | [kimi_k3.py#L3666](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/kimi_k3.py#L3666), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| `Qwen3ForCausalLM` | [`qwen3-32b`](../qwen3-32b.md) | ✓ | ✓ | — | — | [qwen3.py#L718](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3.py#L718), [generative_models.mdx#L63](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/supported-models/generative_models.mdx#L63) |
| `Qwen3MoeForCausalLM` | [`qwen3-235b-a22b`](../qwen3-235b-a22b.md) | ✓ | ✓ | — | `mtp` | [qwen3_moe.py#L1252](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3_moe.py#L1252), [generative_models.mdx#L63](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/supported-models/generative_models.mdx#L63), [model_config.py#L748](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L748) |
| `Qwen3_5ForConditionalGeneration` | [`qwen3.5-27b`](../qwen3.5-27b.md), [`qwen3.6-27b`](../qwen3.6-27b.md), [`qwen3.8-27b`](../qwen3.8-27b.md) | ✓ | _unknown_ | — | `mtp` | [qwen3_5.py#L2690](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3_5.py#L2690), [model_config.py#L771](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L771) |
| `Qwen3_5MoeForConditionalGeneration` | [`qwen3.5-35b-a3b`](../qwen3.5-35b-a3b.md), [`qwen3.6-35b-a3b`](../qwen3.6-35b-a3b.md) | ✓ | _unknown_ | — | `mtp` | [qwen3_5.py#L2690](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3_5.py#L2690), [model_config.py#L156](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L156) |
| `Qwen3_5MoeForCausalLM` | [`qwen3.8-2.4t-a95b`](../qwen3.8-2.4t-a95b.md) | ✓ | _unknown_ | — | `mtp` | [qwen3_5_text.py#L257](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3_5_text.py#L257), [model_config.py#L158](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L158) |
| `Qwen4ExpForConditionalGeneration` | [`qwen3.8-flash-next`](../qwen3.8-flash-next.md) | ✗ | ✗ | — | — | [registry.py](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/registry.py), [models](https://github.com/sgl-project/sglang/tree/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models) |

### Per-model details

| Model record | Since | Reasoning parser | Tool parser | Notes | Evidence |
|---|---|---|---|---|---|
| [`kimi-k2-thinking`](../kimi-k2-thinking.md) | _unknown_ | kimi_k2 | kimi_k2 | The reasoning guide names Kimi K2 Thinking with the kimi_k2 parser and says it also requires --tool-call-parser kimi_k2 for tool use. | [separate_reasoning.mdx#L57](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/separate_reasoning.mdx#L57), [separate_reasoning.mdx#L60](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/separate_reasoning.mdx#L60) |
| [`deepseek-v3.2-exp`](../deepseek-v3.2-exp.md) | _unknown_ | deepseek-v3 | deepseekv31 | The reasoning guide's DeepSeek-V3 series row says 'Including DeepSeek-V3.2' and links deepseek-ai/DeepSeek-V3.2-Exp; the tool parser guide maps DeepSeek-V3.2-Exp to deepseekv31 (deepseekv32 is for DeepSeek-V3.2). | [separate_reasoning.mdx#L42](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/separate_reasoning.mdx#L42), [tool_parser.mdx#L37](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/tool_parser.mdx#L37) |
| [`qwen3-32b`](../qwen3-32b.md) | _unknown_ | qwen3 | _unknown_ | Reasoning guide: 'Standard Qwen3 models' -> qwen3. | [separate_reasoning.mdx#L45](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/separate_reasoning.mdx#L45) |
| [`qwen3-235b-a22b`](../qwen3-235b-a22b.md) | _unknown_ | qwen3 | _unknown_ | Reasoning guide: 'Standard Qwen3 models' -> qwen3. | [separate_reasoning.mdx#L45](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/separate_reasoning.mdx#L45) |
| [`qwen3.8-27b`](../qwen3.8-27b.md) | v0.5.19 | _unknown_ | _unknown_ | Listed under 'New models in this release' (#34859), although the architecture itself was already registered. | [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| [`qwen3.8-2.4t-a95b`](../qwen3.8-2.4t-a95b.md) | v0.5.19 | _unknown_ | _unknown_ | Listed under 'New models in this release' as 'Qwen3.8 (2.4T-A95B)' (#35758). Release notes also register the Qwen3_5 text-only architectures in the mamba radix cache whitelists for Qwen3.8-MXFP4 DCP (#35297). | [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |

### Row notes

- **`DeepseekV3ForCausalLM`** — SGLang's supported-models docs are family-level: the DeepSeek row covers 'v1, v2, v3/R1' and a separate row covers 'Kimi K2 (Thinking, Instruct)'. As a draft, DeepseekV3ForCausalLM is remapped to DeepseekV3ForCausalLMNextN (MTP).
- **`DeepseekV32ForCausalLM`** — Not named in the supported-models family table ('v1, v2, v3/R1'), although the attention backend guide names DeepSeek V3.2 for the DSA backend. Draft remap to DeepseekV3ForCausalLMNextN.
- **`DeepseekV4ForCausalLM`** — Draft selection: when the target config carries dspark_* keys (a DSpark-bundled checkpoint) and the algorithm is unset or DSPARK, the draft loads as DeepseekV4ForCausalLMDSpark; otherwise it loads as DeepseekV4ForCausalLMNextN with num_nextn_predict_layers=1. The code comment reads 'A dspark-bundled checkpoint may also carry MTP layers; the selected algorithm decides which draft arch to load.' Not in the supported-models family table. v0.5.19 release notes carry many DeepSeek-V4 items (W4A8 MXFP4 MoE on Hopper, Q8KV8 sparse MLA prefill, shared-experts fusion, SSD offload).
- **`DeepseekV41ForCausalLM`** — No module under python/sglang/srt/models and no doc mentions the architecture at this commit (verified by git grep against the commit). SGLang v0.5.19 was published 2026-09-05; DeepSeek-V4.1-Flash was released 2026-09-10.
- **`Glm4MoeForCausalLM`** — The supported-models table's GLM rows cover ChatGLM and GLM-4 (9B), not the GLM-4.5/4.6/4.7 MoE line. The tool parser guide maps 'GLM series (e.g. zai-org/GLM-4.6)' to glm without naming GLM-4.7, and a glm47 parser exists in the registry but not in the guide's table, so no per-model parser is recorded. Draft remap to Glm4MoeForCausalLMNextN.
- **`GlmMoeDsaForCausalLM`** — Implemented in glm4_moe.py as a subclass of the DeepSeek-V2 implementation (vLLM places the same architecture in its DeepSeek-V3.2 module). Draft remap to GlmMoeDsaForCausalLMNextN. The HiSparse guide names GLM-5.1 as a DSA model and GLM-5.2's IndexShare as native index reuse; release notes add fused top-k seed remap for disaggregated GLM-5.2 on ROCm (#36714).
- **`Glm5NextForConditionalGeneration`** — No module under python/sglang/srt/models and no doc mentions the architecture at this commit (verified by git grep), yet the v0.5.19 release notes list a 'GLM-5.3 deployment guide' in the cookbook. See open_questions.
- **`KimiK25ForConditionalGeneration`** — A dedicated EAGLE3 / EAGLE3.1 draft with MLA attention exists for Kimi-K2.x (kimi_k25_eagle3.py, naming kimi-k2.5-eagle3-mla and kimi-k2.6-eagle3.1-mla checkpoints). The supported-models table lists Kimi K2 and Kimi-VL, not K2.5/K2.6.
- **`KimiK3ForConditionalGeneration`** — DSpark only on release-note evidence ('[AMD] Improve K3 dspark draft attn kernel perf', #35499); the draft checkpoint source is not stated. Other v0.5.19 K3 items: Kimi-K3 on Ascend A3, MoRI-EP on AMD, FlashInfer MXFP4 MoE auto-selection on SM107.
- **`Qwen3ForCausalLM`** — Supported-models Qwen row lists Qwen/Qwen3-0.6B among its examples. Only LayerNorm sequence parallelism names Qwen3 dense specifically.
- **`Qwen3MoeForCausalLM`** — Supported-models Qwen row lists Qwen/Qwen3-30B-A3B among its examples. As a draft, Qwen3MoeForCausalLM is remapped to Qwen3MoeForCausalLMMTP; whether a Qwen3-235B-A22B checkpoint carries MTP weights is a model-side question.
- **`Qwen3_5ForConditionalGeneration`** — The supported-models Qwen row is a loose 'Qwen3 series' entry whose examples include Qwen3.5-397B-A17B but no dense Qwen3.5 model, so documentation coverage is unknown. Draft remap to Qwen3_5ForCausalLMMTP with num_nextn_predict_layers=1.
- **`Qwen3_5MoeForConditionalGeneration`** — Documentation coverage unknown for the same reason as the dense row (the Qwen3.5-397B-A17B example's architecture is not stated in the docs). Draft remap to Qwen3_5ForCausalLMMTP.
- **`Qwen3_5MoeForCausalLM`** — Text-only Qwen3.5 architecture in qwen3_5_text.py. Draft remap to Qwen3_5ForCausalLMMTP.
- **`Qwen4ExpForConditionalGeneration`** — No module under python/sglang/srt/models and no doc mentions the architecture at this commit (verified by git grep). Qwen3.8-Flash-Next's HF repo was created 2026-08-24, twelve days before v0.5.19; vLLM added it in v0.29.0 (2026-09-09).

## Technique support

| Glossary entry | Implementation | Flags | Since | Evidence |
|---|---|---|---|---|
| [dsa](../../../docs/glossary/dsa.md) | 'dsa' attention backend ('nsa' kept as a deprecated alias) with separate DSA prefill / decode backend selection; DSA top-k kernels. | `--attention-backend dsa` | _unknown_ | [server_args.py#L176](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L176), [attention_backend.mdx#L310](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/attention_backend.mdx#L310), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| [indexshare](../../../docs/glossary/indexshare.md) | Cross-layer top-k reuse read from the model config (index_topk_freq / index_topk_pattern); the HiSparse guide calls it native in GLM-5.2 as IndexShare and prefetches skip layers' working sets automatically. | — | _unknown_ | [model_config.py#L237](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L237), [model_config.py#L241](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L241), [hisparse_guide.mdx#L123](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/hisparse_guide.mdx#L123) |
| [mla](../../../docs/glossary/mla.md) | MLA attention backends flashinfer, flashmla, cutlass_mla, trtllm_mla, cutedsl_mla, tokenspeed_mla (plus Ascend MLA); decode context parallelism stripes the MLA KV cache across ranks. | `--dcp-size N` | _unknown_ | [attention_backend.mdx#L188](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/attention_backend.mdx#L188), [dcp.mdx#L7](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/dcp.mdx#L7) |
| [mtp](../../../docs/glossary/mtp.md) | MTP runs through speculative decoding: the target architecture is remapped to a per-family NextN / MTP draft architecture (DeepseekV3ForCausalLMNextN, DeepseekV4ForCausalLMNextN, GlmMoeDsaForCausalLMNextN, Glm4MoeForCausalLMNextN, Qwen3_5ForCausalLMMTP, Qwen3MoeForCausalLMMTP). | `--speculative-algorithm EAGLE --speculative-num-steps 1 --speculative-eagle-topk 1 --speculative-num-draft-tokens 2 (MiMo example)` | _unknown_ | [speculative_decoding.mdx#L401](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/speculative_decoding.mdx#L401), [model_config.py#L665](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L665), [model_config.py#L771](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L771) |
| [speculative-decoding](../../../docs/glossary/speculative-decoding.md) | Builtin algorithms DFLASH, DSPARK, EAGLE, EAGLE3, FROZEN_KV_MTP, STANDALONE, NGRAM, plus plugin-registered algorithms. DeepSeek-V4 DSpark loads DeepseekV4ForCausalLMDSpark from a checkpoint bundling the dspark_* keys; Kimi-K2.x has a dedicated EAGLE3/EAGLE3.1 MLA draft. | `--speculative-algorithm DSPARK` | _unknown_ | [spec_info.py#L40](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/speculative/spec_info.py#L40), [deepseek_v4_dspark.py#L1100](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v4_dspark.py#L1100), [dspark_config.py#L164](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/speculative/dspark_components/dspark_config.py#L164), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |
| [kda](../../../docs/glossary/kda.md) | Linear-attention kernel backends include flashkda, nvidia_kda and ptx_kda; v0.5.19 adds a fused-accept state advance for FlashInfer KDA MTP verify. | `--linear-attn-kernel-backend (choices include flashkda, nvidia_kda, ptx_kda)` | _unknown_ | [server_args.py#L341](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py#L341), [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19), [generative_models.mdx#L54](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/supported-models/generative_models.mdx#L54) |
| [mhc](../../../docs/glossary/mhc.md) | DeepSeek-V4 mHC handled in the model implementation; v0.5.19 adds an AMD aiter fused mHC post+pre path with cross-layer boundary dispatch. | — | _unknown_ | [release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.19) |

- **dsa** — The attention backend guide says DSA is specifically designed for DeepSeek V3.2. v0.5.19 moves DSA prefill top-k to the v2 kernel (#35175).
- **indexshare** — Unlike vLLM v0.29.0 (which documents the same mechanism behind --hf-overrides use_index_cache for DeepSeek-V3.2), SGLang reads the pattern from the config, which is how GLM-5.2 ships it.
- **mtp** — The MTP guide's example uses --speculative-algorithm EAGLE; the server_args help text lists NEXTN as a builtin algorithm, but NEXTN is not a member of the SpeculativeAlgorithm enum (see open_questions).
- **speculative-decoding** — The speculative decoding guide covers EAGLE-2/3, MTP, DFlash, standalone and NGRAM but does not mention DSpark, while code and release notes do (LFM2 DSpark #31041, multi-adapter LoRA with DSPARK #34337, DSV4 DSpark sample-from-anchor fix #36419) — docs lag code.
- **kda** — The supported-models table's Kimi Linear row describes KDA.
- **mhc** — Only release-note evidence among this snapshot's sources.

## Open questions

- GLM-5.3: the release notes list a 'GLM-5.3 deployment guide' in the cookbook, yet no module or doc at the tag commit mentions Glm5NextForConditionalGeneration (GLM-5.3-Flash's architecture). The cookbook is outside this snapshot's sources; it may cover a different GLM-5.3 checkpoint, a plugin, or support merged after the tag. Registry membership follows code.
- CSA/HCA (DeepSeek-V4): SGLang has a 'dsv4' attention backend (with 'compressed' as a deprecated alias) and the HiSparse guide describes DeepSeek-V4 caches as 'C4 KV', 'c4_indexer' and 'C128 KV' — compression ratios matching CSA (m=4, indexed) and HCA (m'=128) in the DeepSeek-V4 record. That is a stronger hint than vLLM's, but no source names CSA or HCA, so csa-hca stays unasserted.
- server_args help text lists 'NEXTN' among builtin speculative algorithms, but SpeculativeAlgorithm has no NEXTN member (it has FROZEN_KV_MTP); from_string falls back to plugin-registered algorithms. Where NEXTN is mapped is not among this snapshot's sources.
- SGLang's supported-models documentation is family-level and explicitly directs users to search python/sglang/srt/models for an architecture, so `documented` is a weak signal here: DeepSeek V3.2/V4, GLM-4.7/5.x and Kimi K2.5/K3 are served by code but absent from the family table.
- Doc/code gap on DSpark: the speculative decoding guide never mentions DSpark although SpeculativeAlgorithm.DSPARK, a DeepSeek-V4 DSpark draft architecture and several release-note items exist.
- Cross-record note for deepseek-v4-flash-0731: SGLang loads a DeepSeek-V4 DSpark-bundled checkpoint's draft as either DSpark or NextN (num_nextn_predict_layers=1) depending on the chosen algorithm, with the comment that such a checkpoint 'may also carry MTP layers'. That is engine-side evidence bearing on the 0731 record's MTP-vs-DSpark question; the model record is not edited from here.
- Kimi K3 DSpark is evidenced only by an AMD kernel item in the release notes; the draft checkpoint and its activation path are not among the sources (vLLM v0.29.0 likewise recognizes a K3DSparkModel draft).
- RL-facing serving features (engine sleep/wake, weight refit, partial rollout) are documented in sglang_for_rl.mdx but have no engine schema v2 field; revisit when verl (E3) exercises the rollout-backend integration.
- Source reproducibility: release_notes.json is GitHub releases API output with mutable counters, so its sha256 will drift. v0.5.19 is an annotated tag (tag object 59f20bf) — commit_sha is the dereferenced commit 0bcd822.

## Sources

- <https://api.github.com/repos/sgl-project/sglang/releases/tags/v0.5.19>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/registry.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v2.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v4.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v4_dspark.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/glm4_moe.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/kimi_k25.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/kimi_k3.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3_moe.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3_5.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3_5_text.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/speculative/spec_info.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/server_args.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/parser/reasoning_parser.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/function_call/function_call_parser.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/supported-models/generative_models.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/supported-models/multimodal_language_models.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/speculative_decoding.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/attention_backend.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/quantized_kv_cache.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/pd_disaggregation.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/epd_disaggregation.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/hicache_design.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/expert_parallelism.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/pipeline_parallelism.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/dcp.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/separate_reasoning.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/tool_parser.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/hisparse_guide.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/docs/docs/advanced_features/sglang_for_rl.mdx>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/speculative/dspark_components/dspark_config.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_nextn.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/deepseek_v4_nextn.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/glm4_moe_nextn.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/qwen3_5_mtp.py>
- <https://raw.githubusercontent.com/sgl-project/sglang/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/models/kimi_k25_eagle3.py>
