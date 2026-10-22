# MiniMax-Speech-2.8

> 中文版：[minimax-speech-2.8.zh.md](./minimax-speech-2.8.zh.md)

*Media schema version: 1*

## Release identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | MiniMax-Speech-2.8 | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| Family | MiniMax | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| Organization | MiniMax | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| Release date | 2026-01 | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| Openness | closed | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| License | [Unknown/Not Disclosed] | — |
| Variant policy | Hosted Speech 2.8 service announced January 23, 2026. Official announcement links the Open Platform and Audio product; no model checkpoint or self-hosted architecture is disclosed there. This record covers those public capabilities, not an open-weight release. | [source 1](https://www.minimax.io/news/minimax-speech-28) |

## Generation

| Field | Value | Evidence |
|---|---|---|
| Input modalities | text; audio | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| Output modalities | audio | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| Tasks | text-to-speech; voice-cloned text-to-speech | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| Objective | [Unknown/Not Disclosed] | — |
| Scheduler | [Unknown/Not Disclosed] | — |
| Sampling | [Unknown/Not Disclosed] | — |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Backbone | [Unknown/Not Disclosed] | — |
| Parameters | [Unknown/Not Disclosed] | — |
| Attention | [Unknown/Not Disclosed] | — |
| Conditioning | Text includes native sound tags for fillers and nonverbal cues. Vendor describes voice cloning from a 10-second reference sample. Reference audio is conditioning for voice identity, not a claim of unrestricted audio-to-audio generation. | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| VAE | [Unknown/Not Disclosed] | — |
| Audio codec | [Unknown/Not Disclosed] | — |
| Multimodal coupling | [Unknown/Not Disclosed] | — |
| Implementation | Hosted Open Platform API and MiniMax Audio are the access routes named in the announcement. | [source 1](https://www.minimax.io/news/minimax-speech-28) |

## Output

| Field | Value | Evidence |
|---|---|---|
| Resolution | [Unknown/Not Disclosed] | — |
| Frame rate | [Unknown/Not Disclosed] | — |
| Duration | [Unknown/Not Disclosed] | — |
| Audio sample rate | [Unknown/Not Disclosed] | — |
| Audio channels | [Unknown/Not Disclosed] | — |
| Formats | — | — |

## Training

| Field | Value | Evidence |
|---|---|---|
| Training data | [Unknown/Not Disclosed] | — |
| Pretraining | [Unknown/Not Disclosed] | — |
| Post-training | [Unknown/Not Disclosed] | — |

## Precision

| Field | Value | Evidence |
|---|---|---|
| Weight precision | [Unknown/Not Disclosed] | — |
| Compute precision | [Unknown/Not Disclosed] | — |
| Quantization | [Unknown/Not Disclosed] | — |

## Release artifacts and limitations

| Field | Value | Evidence |
|---|---|---|
| Released artifacts | — | — |
| Hosted pipeline scope | Speech 2.8 text-to-speech with native sound tags, voice cloning and cross-lingual improvements is offered through Open Platform and MiniMax Audio. | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| Limitations | Announcement provides capabilities and demos rather than architecture, weights, training details or output-format specifications.; Voice similarity and noise-removal improvements are vendor claims; no runtime or listening evaluation was performed here. | [source 1](https://www.minimax.io/news/minimax-speech-28) |

## Open questions

- Backbone, parameters, training objective/data/optimizer, codec and deployment precision are undisclosed in the registered announcement.
- Sample rate, channels, output formats and request limits need version-specific API evidence before they can be filled.
- Earlier Speech 02 /2.5 /2.6 services remain inventory items; the open Speech test dataset is not a release of model weights.

## Sources

- [Source 1](https://www.minimax.io/news/minimax-speech-28)
