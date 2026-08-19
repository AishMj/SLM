# Learning resources

Curated for this project specifically - C++, small language models, local
inference, video analytics, and the tooling around them.

Opinionated. Where several options exist I have named the one I would actually
start with rather than listing everything.

**Free** unless marked otherwise.

---

## Start here - the 6-week path

If you do nothing else, do these in this order. Roughly 6-8 hours a week.

| Week | What | Why now |
|---|---|---|
| 1 | learncpp.com sections 1-8 | You are writing C++ this month |
| 2 | MIT Missing Semester (shell, git, debugging) | Removes daily friction immediately |
| 3-4 | Karpathy - Neural Networks: Zero to Hero, videos 1-4 | The only thing that makes LLMs stop being magic |
| 5 | Hugging Face NLP Course, chapters 1-3 | Tokenizers, models, the vocabulary everyone uses |
| 6 | Docker - TechWorld with Nana, 3-hour video | You will need to ship this eventually |

Everything after that is depth in whichever direction the work pulls you.

---

## C++

You said you are new to C++. This is the highest-leverage thing on the list,
because everything else in the project assumes it.

| Resource | Format | Notes |
|---|---|---|
| **learncpp.com** | Free, text | **Start here.** The best free C++ course anywhere. Modern C++, well sequenced, exercises included |
| The Cherno - C++ series | Free, YouTube | Excellent for intuition. Watch alongside learncpp, not instead of it |
| cppreference.com | Free, reference | Not a tutorial. The reference you will live in once you can read it |
| A Tour of C++ - Stroustrup | Book, paid | Short, by the language's author. Read after learncpp, not before |
| Beginning C++ Programming - Frank Mitropoulos | Udemy, paid | If you prefer video-led. Long but thorough |

**What you actually need for this project:** `struct`, `std::vector`, `std::set`,
range-for loops, `const&` parameters, and reading a header file. That is
learncpp chapters 1-8 plus 16-17. You do not need templates, inheritance or
move semantics yet.

---

## Computer science fundamentals

Skip if you already have these. Worth it if the ML maths feels shaky.

| Resource | Format | Notes |
|---|---|---|
| **Harvard CS50** | Free, edX + YouTube | The famous one. Genuinely good, and it is in C, which helps C++ |
| MIT Missing Semester | Free, missing.csail.mit.edu | **Do this one.** Shell, git, vim, debugging, profiling. Six hours that pay back weekly |
| MIT 6.006 Algorithms | Free, OCW | Only if you hit algorithmic problems. Not urgent here |

---

## LLMs and small language models

| Resource | Format | Notes |
|---|---|---|
| **Karpathy - Neural Networks: Zero to Hero** | Free, YouTube | **The single best resource in this list.** Builds a GPT from nothing, in code. Video 4 "Let's build GPT" is the one |
| Karpathy - Deep Dive into LLMs | Free, YouTube | 3.5 hours, the whole modern pipeline explained plainly |
| **Build a Large Language Model (From Scratch)** - Raschka | Book, paid | If you prefer reading to watching. Code-first, no hand-waving |
| Hugging Face NLP Course | Free, huggingface.co/learn | Practical. Tokenizers, fine-tuning, the actual libraries |
| Stanford CS224N - NLP with Deep Learning | Free, YouTube + web | University-level. Do after Karpathy, not before |
| Stanford CS336 - Language Modeling from Scratch | Free, web + YouTube | Newer, builds everything end to end. Demanding |
| 3Blue1Brown - Neural Networks / Transformers | Free, YouTube | Best visual intuition for attention. Watch before Karpathy |

**Order I would follow:** 3Blue1Brown transformers video → Karpathy videos 1-4 →
Hugging Face course → CS224N if you want depth.

---

## Running models locally - llama.cpp, quantization, GGUF

Thin on courses. This is a docs-and-forums area.

| Resource | Format | Notes |
|---|---|---|
| **llama.cpp repo docs** | Free | `docs/build.md`, `tools/server/README.md`, and the discussions tab. The real documentation |
| llama.cpp k-quants PR #1684 | Free | Where the quantization quality numbers come from |
| Hugging Face - GGUF docs | Free | Format explanation |
| Maarten Grootendorst - Visual Guide to Quantization | Free, blog | Best explanation of what Q4_K_M actually means |
| r/LocalLLaMA | Free, forum | Where practical local-inference knowledge actually lives |

**Also read:** `LLAMA_CPP_SETUP.md` and `MODEL_DOWNLOADS.md` in this repo. They
were written from actually doing it on your machine, including the traps.

---

## Prompt engineering

| Resource | Format | Notes |
|---|---|---|
| **Anthropic prompt engineering docs** | Free | The clearest vendor guide. Applies broadly, not just to Claude |
| OpenAI Cookbook | Free, GitHub | Practical recipes |
| DeepLearning.AI short courses | Free | 1-2 hours each. "ChatGPT Prompt Engineering for Developers" is the starting one |
| llama.cpp GBNF grammar docs | Free | Constrained decoding. Directly relevant - see `nimbus_lattice/03_determinism.md` |

---

## Fine-tuning - LoRA, QLoRA

| Resource | Format | Notes |
|---|---|---|
| **Hugging Face PEFT docs** | Free | The reference implementation everything else wraps |
| LoRA paper - arxiv 2106.09685 | Free | Short and readable. Worth the hour |
| QLoRA paper - arxiv 2305.14314 | Free | Where the VRAM numbers in our matrix come from |
| Unsloth notebooks | Free, Colab | Fastest way to a working fine-tune. Runs free on Colab |
| Sebastian Raschka - LoRA articles | Free, blog | Best practical explanation of rank, alpha, target modules |

**Start with an Unsloth Colab notebook.** Get one fine-tune working end to end
before reading theory - it makes the theory land.

---

## Computer vision and video analytics

| Resource | Format | Notes |
|---|---|---|
| **Stanford CS231n** | Free, YouTube + notes | The classic CV course. Still the best foundation |
| OpenCV Python tutorials | Free, docs.opencv.org | Concepts transfer to C++ |
| Ultralytics YOLO docs | Free | Detection, tracking, export. Note the AGPL licence issue in our matrix |
| PyImageSearch | Free + paid | Practical, project-shaped tutorials |
| Roboflow blog | Free | Good on modern detection and evaluation |

**Directly relevant to your work:** tracking (`ByteTrack`, `BoT-SORT` papers),
and the MOT metrics - MOTA, IDF1 - since track identity is what your analytics
depend on.

---

## Docker

| Resource | Format | Notes |
|---|---|---|
| **TechWorld with Nana - Docker in 3 hours** | Free, YouTube | **Start here.** Best single Docker video |
| Docker official Get Started | Free, docs.docker.com | Do it after the video, hands-on |
| Docker & Kubernetes: The Practical Guide - Schwarzmüller | Udemy, paid | If you want depth and Kubernetes too |
| Play with Docker | Free, labs.play-with-docker.com | Browser sandbox, nothing to install |

**Why it matters here:** shipping an inference service with a pinned llama.cpp
build and a model file is exactly what containers are for.

---

## Build systems and tooling

| Resource | Format | Notes |
|---|---|---|
| **Modern CMake** - cliutils.gitlab.io/modern-cmake | Free, book | Short, opinionated, correct. CMake tutorials elsewhere teach 2009 CMake |
| Pro Git | Free, git-scm.com/book | The git reference. Chapters 1-3 and 7 |
| MIT Missing Semester | Free | Listed twice on purpose. The shell and debugging lectures especially |

---

## Papers worth reading, in order

Short list. Each one changes how you think.

| Paper | Why |
|---|---|
| Attention Is All You Need - 1706.03762 | The transformer. Read it after Karpathy, it will make sense |
| LoRA - 2106.09685 | Fine-tuning without the cost |
| QLoRA - 2305.14314 | Fine-tuning on one GPU |
| HumanEval / Codex - 2107.03374 | Where code benchmarks come from |
| MultiPL-E - 2208.08227 | Why a Python score says nothing about C++ |
| vLLM / PagedAttention - 2309.06180 | How serving actually scales |

Full reference list with what each one backs: `snorkelbadger_SLM_Matrix.xlsx`,
References section.

---

## What to skip for now

Being honest about what is not worth your time yet:

- **Kubernetes** - not until Docker is comfortable and you have something to scale
- **Training from scratch** - you are fine-tuning at most; the maths is interesting but not on the critical path
- **RAG courses** - your problem is code generation, not retrieval
- **Agent frameworks** - LangChain, AutoGen. Your pipeline is a DAG you control; frameworks would obscure it
- **CUDA programming** - llama.cpp already does this for you

---

## If you only have one hour a week

1. **Karpathy - Let's build GPT from scratch** (2 hours, split it)
2. **MIT Missing Semester - shell and git** (2 hours)
3. **learncpp.com chapters 1-8** (spread over weeks)

Those three cover the largest gaps between where you are and where this project
needs you.
