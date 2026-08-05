# ipoefgfefs SLM Selection

SLM (Small Language Model) selection research and comparison for the ipoefgfefs Workflow Builder.

The SLM generates C++ `custom_logic` block implementations that stitch multiple camera analytics outputs together, cross-compiled for server (x86) and camera (aarch64 / Cortex-A53).

**Current model in use: qwen2.5-coder:14b — BLOCKED (Alibaba/China, NDAA §889 violation). Must be replaced.**

---

## Files

| File | Description |
|---|---|
| `ipoefgfefs_SLM_Matrix.xlsx` | Main deliverable — 14 models x 37 columns comparison table |
| `gen_xl.py` | Python script to regenerate the Excel from source data |
| `GLOSSARY.md` | 50+ term glossary with ipoefgfefs examples and real-world analogies |
| `INFERENCE_ENGINES.md` | llama.cpp vs 15 alternatives — POC to prod decision guide |
| `ADDITIONAL_FACTORS.md` | 10 selection factors beyond benchmarks (cost, privacy, CI/CD, etc.) |
| `SKILLSET_ROADMAP.md` | Priority-ranked learning path with YouTube/Udemy resources |
| `REFERENCES.md` | 32 source papers, GitHub repos, and leaderboards with URLs |

---

## Compliance Tiers

| Tier | Meaning | Examples |
|---|---|---|
| FULL | US company + Apache 2.0/MIT | Phi-4 (Microsoft), Granite (IBM), Llama (Meta) |
| ALLY | EU/Canada + open license | Devstral (Mistral AI, France), Mistral 7B |
| COMMERCIAL | Restrictive ToS - needs legal review | Codestral, Gemma (Google ToS) |
| BLOCKED | China/Russia origin - CANNOT USE | Qwen (Alibaba), DeepSeek, InternLM |

---

## Top Picks

| Use Case | Model | Why |
|---|---|---|
| Server codegen | Devstral Small 24B | Best C++ quality, Apache 2.0, 128K context |
| Budget | Granite 3.3 Code 8B | IBM US, Apache 2.0, FIM, fits 12GB GPU |
| Best accuracy | Llama 3.3 70B | Highest benchmarks, needs 2xA100 |
| Edge / camera | Phi-3.5-mini 3.8B | Only model fitting Cortex-A53 at 2.4GB Q4 |

---

## Regenerate Excel

```bash
pip install openpyxl
python3 gen_xl.py
```
