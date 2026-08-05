# References — ipoefgfefs SLM Selection

All sources used for benchmark data, model specs, and technical claims in the SLM matrix.

---

## Benchmark Papers

| # | Authors | Title | Year | URL |
|---|---|---|---|---|
| 1 | Chen et al. | HumanEval — Evaluating Large Language Models Trained on Code | 2021 | arxiv.org/abs/2107.03374 |
| 2 | Cassano et al. | MultiPL-E: A Scalable and Polyglot Approach to Benchmarking Neural Code Generation | 2022 | arxiv.org/abs/2208.08227 |
| 3 | Austin et al. | Program Synthesis with Large Language Models (MBPP) | 2021 | arxiv.org/abs/2108.07732 |
| 4 | Zhuo et al. | BigCodeBench: Benchmarking Code Generation with Diverse Function Calls and Complex Instructions | 2024 | arxiv.org/abs/2406.15877 |
| 5 | Hendrycks et al. | Measuring Massive Multitask Language Understanding (MMLU) | 2021 | arxiv.org/abs/2009.03300 |

---

## Model Papers & Announcements

| # | Source | Title | Year | URL |
|---|---|---|---|---|
| 6 | Microsoft Research | Phi-4 Technical Report | 2024 | arxiv.org/abs/2412.08905 |
| 7 | Microsoft Research | Phi-3 Technical Report | 2024 | arxiv.org/abs/2404.14219 |
| 8 | Meta AI | The Llama 3 Herd of Models | 2024 | arxiv.org/abs/2407.21783 |
| 9 | Roziere et al. | Code Llama: Open Foundation Models for Code | 2023 | arxiv.org/abs/2308.12950 |
| 10 | Lozhkov et al. | StarCoder 2 and The Stack v2 | 2024 | arxiv.org/abs/2402.19173 |
| 11 | Mistral AI | Devstral: A Code Agent Model | 2025 | mistral.ai/news/devstral |
| 12 | Mistral AI | Codestral: Hello, World! | 2024 | mistral.ai/news/codestral |
| 13 | Jiang et al. | Mistral 7B | 2023 | arxiv.org/abs/2310.06825 |
| 14 | IBM Research | Granite 3.3 Code Models | 2025 | research.ibm.com/blog/granite-3-code |
| 15 | Google DeepMind | Gemma 3 Technical Report | 2025 | arxiv.org/abs/2503.19786 |

---

## Fine-Tuning Methods

| # | Authors | Title | Year | URL |
|---|---|---|---|---|
| 16 | Hu et al. | LoRA: Low-Rank Adaptation of Large Language Models | 2021 | arxiv.org/abs/2106.09685 |
| 17 | Dettmers et al. | QLoRA: Efficient Finetuning of Quantized LLMs | 2023 | arxiv.org/abs/2305.14314 |
| 18 | Rafailov et al. | Direct Preference Optimization (DPO) | 2023 | arxiv.org/abs/2305.18290 |

---

## Inference Engines

| # | Source | Title | URL |
|---|---|---|---|
| 19 | Georgi Gerganov | llama.cpp — LLM inference in C/C++ | github.com/ggerganov/llama.cpp |
| 20 | Georgi Gerganov | GGUF Format Specification | github.com/ggerganov/ggml/blob/master/docs/gguf.md |
| 21 | Kwon et al. | Efficient Memory Management for LLM Serving with PagedAttention (vLLM) | arxiv.org/abs/2309.06180 |
| 22 | Zheng et al. | SGLang: Efficient Execution of Structured Language Model Programs | arxiv.org/abs/2312.07104 |
| 23 | HuggingFace | Text Generation Inference (TGI) | github.com/huggingface/text-generation-inference |
| 24 | Dao et al. | FlashAttention: Fast and Memory-Efficient Exact Attention | 2022 | arxiv.org/abs/2205.14135 |

---

## Compliance & Licensing

| # | Source | Title | URL |
|---|---|---|---|
| 25 | US Congress | NDAA §889 — National Defense Authorization Act 2019 | acquisition.gov/FAR/part-4 |
| 26 | BigCode Project | BigCode OpenRAIL-M License | bigcode-project.org/docs/pages/bigcode-openrail |
| 27 | Meta AI | Llama 3 Community License Agreement | llama.meta.com/llama3/license |
| 28 | Google | Gemma Terms of Use | ai.google.dev/gemma/terms |
| 29 | Mistral AI | Codestral License | mistral.ai/licenses/MNPL-0.1.md |

---

## Leaderboards & Live Data

| # | Source | What it tracks | URL |
|---|---|---|---|
| 30 | HuggingFace | Open LLM Leaderboard — live benchmark scores | huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard |
| 31 | BigCode | BigCodeBench Leaderboard | huggingface.co/spaces/bigcode/bigcodebench-leaderboard |
| 32 | EvalPlus | EvalPlus Leaderboard — HumanEval+ | evalplus.github.io/leaderboard.html |

---

## Notes on Benchmark Reliability

- HumanEval scores are Python-based. C++ scores (MultiPL-E) are estimated from translation and may differ.
- MMLU scores used for reasoning ratings are from published papers where available; estimated from model size and training data description where not published.
- tok/s figures are estimates based on community benchmarks at the stated GPU/quantization level. Actual performance depends on server CPU, RAM bandwidth, batch size, and llama.cpp version.
- All data reflects publicly available information as of August 2026.
