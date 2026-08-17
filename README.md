# snorkelbadger SLM Selection

Small language model selection for the snorkelbadger Workflow Builder.

The SLM generates C++ `custom_logic` block implementations that stitch multiple camera analytics
outputs together, cross-compiled for server (x86 Ubuntu) and camera (Ambarella S50, Cortex-A53, aarch64).

**Current model in use: `qwen2.5-coder:14b` — being replaced. See the Recommendation sheet.**

---

## Scope

This workbook covers **small language models only** — 19 models, 76 rows.

Vision encoders, video encoders, text-embedding models, ASR, diffusion, object detectors,
re-ID networks and OCR pipelines were removed. They are the analytics whose outputs
`custom_logic` stitches together, not candidates to replace the code generator.
Everything removed is on the **Excluded** sheet with the reason.

---

## What counts as an SLM here

| Rule | Applied as |
|---|---|
| Must be a generative language model | Has a tokenizer, a context window, produces tokens |
| Dense params ≤ 16B | Phi-4 14B in; Devstral 24B, Codestral 22B, CodeLlama 34B, Qwen2.5 32B, Llama 3.3 70B out |
| MoE judged on active params | DeepSeek-Coder-V2-Lite in (2.4B active); gpt-oss-20b out (21B total) |
| Multimodal kept, labelled separately | `SLM Class` column: text only / multimodal (VLM) / MoE |
| Encoder-only excluded | BGE-M3, Nomic-Embed, all-MiniLM — no generation head |

There is no formal SLM definition. The common cutoff is under 10B, stretched to ~15B.
StarCoder2 15B is actually 16.0B and is flagged as borderline in the sheet.

---

## The 19 models

**Text only (11)** — Qwen2.5-Coder 7B · Phi-4 14B · Granite 3.3 8B · Llama 3.1 8B ·
StarCoder2 15B · CodeGemma 7B · Mistral 7B · Phi-3.5-mini 3.8B · Llama 3.2 3B ·
DeepSeek-R1-Distill-Qwen-14B

**Multimodal / VLM (7)** — Gemma 3 4B · Phi-3.5-Vision 4.2B · Qwen2-VL 7B ·
Llama 3.2 11B Vision · InternVL2 8B · LLaVA-1.6 13B · PaliGemma 3B · Moondream2 1.9B

**MoE (1)** — DeepSeek-Coder-V2-Lite (15.7B total, 2.4B active)

---

## Files

| File | Description |
|---|---|
| `snorkelbadger_SLM_Matrix.xlsx` | Main deliverable — 76 rows, 27 columns, 8 sheets |
| `gen_xl.py` | Python script to regenerate the Excel from source data |
| `GLOSSARY.md` | 50+ term glossary with snorkelbadger examples |
| `INFERENCE_ENGINES.md` | llama.cpp vs alternatives — POC to prod decision guide |
| `ADDITIONAL_FACTORS.md` | 10 selection factors beyond benchmarks |
| `SKILLSET_ROADMAP.md` | Priority-ranked learning path |
| `REFERENCES.md` | Source papers, repos, and leaderboards |

## Excel sheets

| Sheet | Contents |
|---|---|
| SLM Matrix | Every model, one row **per quantization** (Q4_K_M / Q5_K_M / Q8_0 / F16) |
| SLM Definition | The inclusion rules and why each one exists |
| Excluded | Every model removed, with the reason and what it was for |
| Task Categories | The 4 categories present, and which metrics apply to each |
| Inference Engines | 13 LLM-serving engines — hardware support from official docs |
| Fine-Tuning | Full FT / LoRA / QLoRA / DoRA VRAM at 3B / 4B / 8B / 14B |
| Recommendation | Ranked top 3 + edge and serving notes |
| References | 56 sources, tagged by type |

---

## Sourcing rules

Every number carries a bracket tag saying where it came from. Nothing is inferred silently.

| Tag | Meaning |
|---|---|
| `[P: arxiv XXXX.XXXXX Tbl N]` | Peer-reviewed paper, exact table |
| `[MB: ...]` | Official model blog / announcement |
| `[HF: ...]` | HuggingFace model card |
| `[LB: ...]` | Public leaderboard — **no paper exists for this number** |
| `[LL: ...]` | llama.cpp family documentation |
| `[Calc: ...]` | Computed, with the formula stated |

File sizes use the llama.cpp quant spec (Q4_K_M 4.5 bits/param, Q5_K_M 5.5, Q8_0 8.5, F16 16).

Max GPU VRAM is weights + KV cache, where
`KV = 2 * layers * kv_heads * head_dim * seq_len * 2 bytes`, architecture taken from the paper
or `config.json`. Both an 8K figure (the actual snorkelbadger prompt size) and a full-context figure
are given, because the gap is large — Llama 3.1 8B Q4 is 5.2 GB at 8K but 13.1 GB at 128K.

Token rates are **calculated from memory bandwidth, not measured**:
RTX 4090 = 1008 GB/s at 70% efficiency, DDR5 dual channel = 80 GB/s at 60%.
No paper publishes tok/s, so these are tagged as calculated everywhere they appear.

Where a number genuinely does not exist it says `NA` and why — most models never publish
MultiPL-E C++ at all, and Mistral 7B's HumanEval is leaderboard-only.

---

## Context window warning

The snorkelbadger prompt is 6–8K tokens. These leave little or no room for generated output:

CodeGemma 7B (8K) · InternVL2 8B (8K) · PaliGemma 3B (8K) · LLaVA-1.6 (4K) · Moondream2 (2K)

Flagged amber in the Context Window column.

---

## Regenerate Excel

```bash
pip install openpyxl
python3 gen_xl.py
```
