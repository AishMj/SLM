# Skillset Roadmap — ipoefgfefs SLM Engineer

Skills needed to own the SLM selection, deployment, and fine-tuning pipeline. Priority-ranked.

---

## Priority 1 — Do These First (Core for ipoefgfefs Phase 1)

### C++ (C++14, OpenCV)
**Why:** You are generating, reviewing, and debugging C++ code. You need to read the output and know when it's wrong.

**What to learn:**
- C++14 standard features and what's NOT in C++14 (no structured bindings, no std::optional)
- OpenCV 4.x Mat, matchTemplate, minMaxLoc, resize patterns
- Shared library (.so) compilation, symbol visibility
- Cross-compilation basics (aarch64-linux-gnu-g++)

**Resources:**
- YouTube: "The Cherno C++" — free, 100+ videos, practical focus → search "The Cherno C++ series"
- YouTube: "OpenCV C++ Tutorial" by Nicolai Nielsen
- Book: "A Tour of C++" by Bjarne Stroustrup (short, C++14 focused)

---

### llama.cpp (internals + deployment)
**Why:** This is your production inference engine. You need to build it, configure it for GPU, and call it from Python.

**What to learn:**
- Build from source with CUDA support
- GGUF model loading and quantization options
- `n_gpu_layers`, `n_ctx`, `temperature` parameters
- llama-cpp-python Python bindings
- Chat templates per model family

**Resources:**
- GitHub: github.com/ggerganov/llama.cpp — README and examples/ directory
- YouTube: "Run LLMs Locally with llama.cpp" by Fahd Mirza
- YouTube: "llama.cpp GPU setup" by Matt Williams
- llama.cpp wiki: github.com/ggerganov/llama.cpp/wiki

---

### Prompt Engineering for Code Generation
**Why:** The quality of SLM output directly depends on how you write the prompt. This is the fastest way to improve compile success rate.

**What to learn:**
- System prompt vs user prompt structure
- Few-shot examples in prompts
- Chain-of-thought for Pass A (IR planning)
- Constrained output formatting
- Temperature and sampling parameters

**Resources:**
- Course: "ChatGPT Prompt Engineering for Developers" by DeepLearning.AI + OpenAI — free at learn.deeplearning.ai
- GitHub: github.com/openai/openai-cookbook — prompt patterns
- Paper: "Chain of Thought Prompting" (Wei et al. 2022) — arxiv.org/abs/2201.11903

---

## Priority 2 — Next 3 Months (Phase 2 Fine-Tuning)

### LoRA / QLoRA Fine-Tuning
**Why:** Phase 2 of ipoefgfefs plan — fine-tune on your own C++ pairs to push compile success rate from ~68% to ~90%+.

**What to learn:**
- LoRA theory (rank, alpha parameters)
- QLoRA setup with bitsandbytes
- HuggingFace `trl` SFTTrainer
- Dataset formatting (instruction, input, output)
- Evaluating fine-tuned model vs base model

**Resources:**
- YouTube: "Fine-tune LLMs with QLoRA — Practical Guide" by Maxime Labonne → search his name on YouTube
- Course: "Finetuning Large Language Models" by DeepLearning.AI — free at learn.deeplearning.ai
- GitHub: github.com/huggingface/trl — training library with examples
- Blog: "A Beginner's Guide to LLM Fine-Tuning" by Maxime Labonne on Medium

---

### Python (ML Pipelines)
**Why:** All your scripts (codegen.py, feedback_loop.py, gen_slm_prompt.py, gen_xl.py) are Python. Also fine-tuning uses Python.

**What to learn:**
- subprocess, pathlib, json — already using these
- HuggingFace transformers and datasets libraries
- pandas for dataset preparation
- pytest for gate testing

**Resources:**
- Udemy: "Complete Python Bootcamp" by Jose Portilla — udemy.com (search the title)
- HuggingFace course: huggingface.co/learn/nlp-course — free, covers transformers library

---

### GGUF + Quantization Pipeline
**Why:** After fine-tuning, you need to convert LoRA adapter → merged model → GGUF → quantized for deployment.

**What to learn:**
- LoRA merge (`peft` library)
- `convert-hf-to-gguf.py` script (in llama.cpp repo)
- `llama-quantize` tool for Q4_K_M, Q8_0
- Perplexity testing to validate quantization quality

**Resources:**
- llama.cpp wiki: "Converting models" section
- YouTube: "Convert and Quantize LLMs with llama.cpp" — search on YouTube
- Blog: "GGUF Everything" by TheBloke (HuggingFace page)

---

## Priority 3 — 6 Months (Scale + Infrastructure)

### Linux / Cross-Compilation / CMake
**Why:** Build llama.cpp from source, cross-compile pipeline.so for aarch64, manage server dependencies.

**What to learn:**
- CMake build system
- aarch64-linux-gnu toolchain setup
- pkg-config, shared library linking
- systemd service management (keep SLM server running)

**Resources:**
- YouTube: "Embedded Linux cross-compilation" by bootlin — search "bootlin cross compilation"
- YouTube: "CMake Tutorial" by Code, Tech, and Tutorials
- Book: "Linux Command Line" by William Shotts — free at linuxcommand.org

---

### Docker / CI/CD Basics
**Why:** Containerize the SLM server for consistent deployment. Automate regression testing on every commit.

**What to learn:**
- Dockerfile for Flask + llama.cpp + CUDA
- GitHub Actions workflow for compile gate testing
- Docker GPU passthrough (--gpus all)

**Resources:**
- Udemy: "Docker and Kubernetes: The Complete Guide" by Stephen Grider
- YouTube: "GitHub Actions Tutorial" by TechWorld with Nana
- Official Docker docs: docs.docker.com

---

### SLM Benchmarking
**Why:** Objectively compare models before and after fine-tuning. Know if your changes improved things.

**What to learn:**
- Running HumanEval and MultiPL-E locally
- BigCodeBench evaluation
- Building a ipoefgfefs-specific benchmark (compile gate pass rate as the metric)

**Resources:**
- GitHub: github.com/openai/human-eval — run HumanEval locally
- GitHub: github.com/bigcode-project/bigcodebench
- HuggingFace: huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard — live scores

---

### MQTT + ONVIF Basics
**Why:** Understand what the camera sends to the pipeline — helps you write better custom_logic block specs for the SLM.

**What to learn:**
- MQTT pub/sub model, QoS levels
- Mosquitto broker setup
- ONVIF event XML structure
- How loitering/face events are structured

**Resources:**
- YouTube: "MQTT Explained in 10 Minutes" by Steve's Internet Guide — search on YouTube
- ONVIF developer guide: developer.onvif.org
- YouTube: "Mosquitto MQTT Broker Setup" by MQTT tutorials

---

## University-Level Courses (Free)

| Course | What you learn | Where |
|---|---|---|
| Stanford CS229 (Machine Learning) | Foundations of ML, backpropagation | youtube.com — search "Stanford CS229 2023" |
| Stanford CS224N (NLP with Deep Learning) | Transformers, attention, language models | youtube.com — search "Stanford CS224N" |
| MIT 6.S191 (Deep Learning) | Neural nets, CNNs, sequence models | youtube.com — search "MIT 6.S191" |
| Fast.ai Practical Deep Learning | Hands-on, top-down, real projects | fast.ai (completely free) |
| DeepLearning.AI Short Courses | Prompt engineering, fine-tuning, RAG | learn.deeplearning.ai (most free) |

---

## Learning Path Timeline

```
Month 1-2:  C++ + OpenCV + llama.cpp + Prompt Engineering
            → Can fix SLM output bugs, tune prompts, improve gate pass rate

Month 3-4:  Python ML pipelines + QLoRA + GGUF pipeline
            → Can run Phase 2 fine-tuning, evaluate models, deploy fine-tuned models

Month 5-6:  Linux/CMake + Docker + CI/CD + Benchmarking
            → Can automate the entire codegen pipeline, run regression tests, containerize

Month 7+:   Stanford CS224N + Fast.ai
            → Understand WHY models work the way they do, design better FT strategies
```
