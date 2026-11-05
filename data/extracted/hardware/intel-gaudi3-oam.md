# Intel Gaudi 3 OAM

> 中文版：[intel-gaudi3-oam.zh.md](./intel-gaudi3-oam.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | Intel Gaudi 3 OAM | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Vendor | Intel | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Accelerator type | ASIC | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Variant | HL-325L OAM | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Form factor | OCP OAM 2.0 mezzanine module | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Record scope | per_accelerator | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Device count | 1 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Snapshot date | 2026-10-22 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | Gaudi 3 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3) |
| Process | TSMC 5 nm | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=2) |
| Compute units | 2 compute dies; 8 MMEs and 64 TPCs in total. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3) |
| Cache | 96 MB SRAM configurable as unified L3 or four 24 MB L2 slices. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| On-chip memory | 96 MB SRAM | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| Execution model | MMEs for matrix operations; programmable TPCs use VLIW SIMD. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3) |
| Notes | — | — |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | 8 HBM2e devices | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| Capacity (GB) | 128.0 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| Capacity (GiB) | [Unknown/Not Disclosed] | — |
| Bandwidth (TB/s) | 3.7 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| Scope | per_accelerator | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| Notes | — | — |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | Exact rates follow Table 5; the introduction separately rounds BF16/FP8 capability to 1.8 PFLOP/s. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=2), [source 2](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| FP8 | matrix | 1678.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| BF16 | matrix | 1678.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP16 (signed) | matrix | 459.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| TF32 | matrix | 459.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP32 | matrix | 229.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP8 | vector | 57.3 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| BF16 | vector | 28.7 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP16 | vector | 28.7 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP32 | vector | 14.3 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | PCIe Gen5 x16, 128 GB/s bidirectional total (64 GB/s per direction). | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3) |
| Scale up | 24x200 Gbit/s Ethernet RDMA ports; total networking 1200 GB/s bidirectional. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3), [source 2](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=18) |
| Scale out | Three 200 Gbit/s ports per OAM routed for scale-out in the HLB-325 baseboard. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Topology | HLB-325 baseboard: eight OAMs all-to-all using 21 ports per module, with three remaining ports for scale-out. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | 900.0 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Scope | per_accelerator | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| Notes | HL-325L OAM supports up to 900 W Total Device Power with passive or liquid cooling. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | Intel Gaudi software suite with PyTorch integration. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=19) |
| ISA | [Unknown/Not Disclosed] | — |
| Programming model | Graph compiler, kernel fusion, kernel libraries and programmable TPC kernels. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=19) |

## Published measurements

No published measurements recorded.

## Open questions

- Table 5 does not specify sparse/dense conditions, accumulation precision, clock or FMA counting.

## Sources

- [Source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf)
