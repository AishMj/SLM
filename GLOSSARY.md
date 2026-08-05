# SLM Terminology Glossary — ipoefgfefs Workflow Builder

All terms used in SLM selection, deployment, and fine-tuning for the ipoefgfefs project.
Each term includes a ipoefgfefs-specific example and a real-world analogy.

---

## Core Concepts

**SLM (Small Language Model)**
A language model under ~20B parameters, designed to run on a single GPU or CPU server.
- *ipoefgfefs:* Devstral 24B or Granite 8B running on the Ubuntu compile server, generating C++ for the `custom_logic` block.
- *Real world:* GitHub Copilot's autocomplete engine inside your IDE.

**LLM (Large Language Model)**
A language model above ~70B parameters, usually requiring multi-GPU infra or cloud API.
- *ipoefgfefs:* Llama 3.3 70B — only viable on 2×A100 server, used for highest-accuracy code if infra allows.
- *Real world:* GPT-4, Claude Opus — cloud-hosted, too large for on-prem single GPU.

**Base Model**
A model trained on raw text/code data only, with no instruction-following training.
- *ipoefgfefs:* Starcoder2 15B in base form — it predicts the next token but won't follow "write a C++ function that..." instructions well.
- *Real world:* A medical student who has read every textbook but hasn't seen patients yet.

**Instruction-Tuned Model**
A base model further trained to follow human instructions (via RLHF, DPO, or SFT).
- *ipoefgfefs:* Devstral Small 24B instruct — you tell it "write a `process_frame()` method" and it actually does it.
- *Real world:* Same medical student after completing residency — now they respond to patients appropriately.

---

## Model Format & Quantization

**GGUF**
llama.cpp's binary format for storing model weights and quantization metadata in a single file.
- *ipoefgfefs:* `devstral-small-24b-Q4_K_M.gguf` — the file you download and point llama.cpp at.
- *Real world:* An executable `.exe` file — self-contained, run it directly without extra setup.

**GGML**
The predecessor to GGUF. Older format, mostly replaced. Some older models still distributed as GGML.
- *ipoefgfefs:* You won't encounter this for the 10 models in our table — all use GGUF.
- *Real world:* `.mp3` vs `.flac` — GGUF is the modern replacement.

**Q4_K_M**
4-bit quantization using K-means calibration, medium accuracy variant. Best balance of size and quality.
- *ipoefgfefs:* Devstral 24B → 48 GB (F16) compressed to 14 GB (Q4_K_M). Used for production deployment on server.
- *Real world:* High-quality JPEG compression of a photo — significant size reduction, barely noticeable quality loss.

**Q8_0**
8-bit quantization, near-lossless. ~2× the size of Q4 but very close to original model quality.
- *ipoefgfefs:* Use Q8 when compile success rate with Q4 is not good enough — trades RAM for accuracy.
- *Real world:* PNG compression — lossless but larger file.

**F16 / BF16**
Full 16-bit floating point — no compression, original model quality. Needs the most RAM.
- *ipoefgfefs:* F16 Devstral = 48 GB. Only use for fine-tuning, not inference.
- *Real world:* The original RAW photo file before any compression.

**INT4 / INT8**
Integer quantization formats used by GPU-specific frameworks (TensorRT, ExLlamaV2). Different from GGUF Q4/Q8.
- *ipoefgfefs:* TensorRT-LLM uses INT8 for A100 deployment — not relevant until you get A100 infra.
- *Real world:* Different compression algorithm for the same goal (file size reduction).

**Perplexity**
How "surprised" a model is by test text. Lower = better. Used to measure quantization quality loss.
- *ipoefgfefs:* Q4_K_M typically adds <0.5 perplexity vs F16 — acceptable quality loss.
- *Real world:* Typo rate in written text — lower means the model "understands" the text better.

---

## Fine-Tuning

**Fine-Tuning**
Further training a pre-trained model on your specific data so it learns your patterns.
- *ipoefgfefs:* Training Devstral on 5,000 pairs of (workflow.json → correct C++ output) so it learns your block naming, OpenCV patterns, and C++14 constraints.
- *Real world:* A chef trained in French cuisine doing a 2-week course on Japanese food — keeps all existing skills, adds domain-specific ones.

**LoRA (Low-Rank Adaptation)**
Fine-tune only small "adapter" matrices attached to key model layers, freeze everything else.
- *ipoefgfefs:* Train a LoRA adapter on your C++ pairs. The 24B base weights stay frozen; only the adapter (~50 MB) changes.
- *Real world:* Adding a specialist module to an existing product without redesigning the whole product.

**QLoRA (Quantized LoRA)**
LoRA where the frozen base model is also quantized to 4-bit during training — dramatically reduces GPU RAM needed.
- *ipoefgfefs:* QLoRA lets you fine-tune Devstral 24B on a single A10G 24GB GPU instead of needing 4×A100.
- *Real world:* Same as LoRA but the base product is stored compressed in a warehouse while you work on the module.

**PEFT (Parameter-Efficient Fine-Tuning)**
Umbrella term covering LoRA, QLoRA, DoRA, and other methods that train only a small subset of parameters.
- *ipoefgfefs:* Phase 2 fine-tuning plan uses PEFT (specifically QLoRA) on HuggingFace `trl` library.
- *Real world:* Renovating only the kitchen of a house rather than rebuilding the whole house.

**DPO (Direct Preference Optimization)**
Fine-tuning technique that teaches the model to prefer good outputs over bad ones using ranked pairs.
- *ipoefgfefs:* Phase 3 optional — show the model pairs of (code that compiled, code that failed) so it learns to prefer compilable C++.
- *Real world:* Code review with explicit "this is better than that" feedback instead of just "fix this bug."

**SFT (Supervised Fine-Tuning)**
Standard fine-tuning where you give the model input-output pairs and train it to produce the correct output.
- *ipoefgfefs:* Phase 2 training on (prompt → correct C++ function) pairs collected from successful compile runs.
- *Real world:* Teaching with worked examples — show input, show correct answer, repeat.

**Training Pairs / Dataset**
The (input, output) examples used for fine-tuning.
- *ipoefgfefs:* Each pair = one workflow.json context + the correct C++ `process_frame()` implementation that compiled and passed all 5 gates.
- *Real world:* Flash cards for an exam — question on one side, correct answer on the other.

**Overfitting**
When a model memorizes training data instead of learning general patterns — performs great on training set, fails on new inputs.
- *ipoefgfefs:* If you fine-tune only on loitering+face-match examples, the model may fail on LPR+intrusion workflows it hasn't seen.
- *Real world:* A student who memorizes past exam questions verbatim but can't answer a rephrased question.

---

## Inference & Performance

**TTFT (Time To First Token)**
How long from sending your prompt until the model starts generating the first token of output.
- *ipoefgfefs:* With 8K prompt, TTFT on CPU = 3–5 seconds (reading all tokens). SGLang prefix caching reduces this to ~0.2s for repeated prompts.
- *Real world:* How long a search engine takes to show the first result after you press Enter.

**tok/s (Tokens Per Second)**
How fast the model generates output tokens after TTFT.
- *ipoefgfefs:* Devstral 24B on RTX 3090 = ~30 tok/s. A 400-token C++ function takes ~13 seconds.
- *Real world:* Words per minute for typing — higher is faster.

**Context Window**
Maximum number of tokens the model can process in one request (prompt + output combined).
- *ipoefgfefs:* ipoefgfefs prompts are ~8K tokens (headers + workflow JSON + instructions). Need context window >16K. Devstral has 128K — safe.
- *Real world:* Working memory — how much information you can hold in your head at once.

**KV Cache (Key-Value Cache)**
Memory that stores the model's attention computations for past tokens to avoid recomputing them.
- *ipoefgfefs:* An 8K token prompt with Devstral 24B fills ~1.5 GB of KV cache in GPU VRAM. This is IN ADDITION to model weights.
- *Real world:* Browser cache — stores pages you've visited so they load faster on revisit.

**Prefix Caching**
Reusing KV cache across requests that share the same prompt prefix.
- *ipoefgfefs:* Every ipoefgfefs compile prompt starts with the same 6K tokens (system instructions + C++ headers). SGLang caches this once, TTFT drops from 4s to 0.2s.
- *Real world:* A receptionist who remembers your name and company after the first visit — doesn't ask again.

**Flash Attention**
Memory-efficient attention algorithm that computes attention in tiles, reducing VRAM usage.
- *ipoefgfefs:* llama.cpp uses Flash Attention automatically on Ampere+ GPUs. Essential for 128K context without OOM errors.
- *Real world:* Reading a book by chapter instead of scanning the whole book at once — same result, less desk space needed.

**VRAM (Video RAM)**
GPU memory — separate from system RAM, much faster, much smaller.
- *ipoefgfefs:* RTX 3090 has 24 GB VRAM. Devstral 24B Q4 needs 16 GB VRAM. 8 GB left for KV cache and batch overhead.
- *Real world:* The fast scratch pad on your desk vs the filing cabinet across the room (system RAM).

---

## Hardware

**CUDA**
NVIDIA's GPU programming platform — what most ML frameworks use to run on NVIDIA GPUs.
- *ipoefgfefs:* llama.cpp compiles with CUDA support for RTX/A100. Flag: `-DLLAMA_CUDA=ON` in cmake.
- *Real world:* The instruction set that lets software talk to NVIDIA GPUs (like x86 for Intel CPUs).

**CUDA sm_XX (Compute Capability)**
NVIDIA GPU generation identifier. Higher = more features and better performance.
- *ipoefgfefs:* sm_60 = GTX 1080 (min for most models), sm_70 = V100/RTX 20xx, sm_80 = A100/RTX 30xx (best).
- *Real world:* CPU instruction sets — SSE4, AVX2, AVX-512 — higher = more capable.

**ROCm**
AMD's GPU compute platform — AMD's equivalent of CUDA.
- *ipoefgfefs:* If the compile server has an AMD RX 7900 XTX, build llama.cpp with `-DLLAMA_HIPBLAS=ON` for ROCm.
- *Real world:* AMD's answer to NVIDIA CUDA — same purpose, different vendor.

**NEON SIMD**
ARM's 128-bit vector instruction set — accelerates matrix math on ARM CPUs.
- *ipoefgfefs:* llama.cpp auto-detects and uses NEON on the Ambarella S50 Cortex-A53, giving ~2–4× speedup vs scalar math.
- *Real world:* SSE2/AVX on Intel — parallel processing of multiple numbers at once.

**aarch64**
64-bit ARM architecture instruction set. The target ISA for the Ambarella S50 camera.
- *ipoefgfefs:* Cross-compile command: `aarch64-linux-gnu-g++ -std=c++14 -o pipeline.so ...`
- *Real world:* x86_64 is Intel/AMD; aarch64 is ARM — different instruction sets, need different compilers.

**Cortex-A53**
ARM CPU core used in the Ambarella S50 camera SoC. In-order execution, lower performance than A73.
- *ipoefgfefs:* Camera SoC — runs compiled `pipeline.so`, NOT the SLM. ~1.2 GHz, LPDDR4 ~20 GB/s bandwidth.
- *Real world:* A Raspberry Pi class processor — capable but not fast.

**LPDDR4**
Low-Power DDR4 RAM, used in mobile and embedded devices including the Ambarella S50.
- *ipoefgfefs:* Camera has LPDDR4 at ~20–25 GB/s bandwidth. This limits tok/s for any edge SLM — memory bound, not compute bound.
- *Real world:* Laptop RAM vs desktop DDR5 — lower bandwidth, lower power.

---

## Benchmarks

**HumanEval**
164 Python coding problems from OpenAI. Model generates code, tests check if it runs correctly. Reported as pass@1 (first attempt success rate).
- *ipoefgfefs:* Proxy for code quality. Devstral 24B = ~68%. Llama 3.3 70B = ~88.4%.
- *Real world:* A coding test score — what percentage of problems did you solve correctly on first try.

**MultiPL-E C++**
HumanEval problems translated to C++. More directly relevant than Python HumanEval for ipoefgfefs.
- *ipoefgfefs:* This is the most important benchmark — directly measures C++ generation quality. Codestral 22B = ~76% (best among compliant).
- *Real world:* Same coding test but the exam is in C++ instead of Python.

**MBPP (Mostly Basic Programming Problems)**
500 simpler coding problems, broader coverage than HumanEval.
- *ipoefgfefs:* Secondary signal. Llama 3.3 70B = ~87%.
- *Real world:* A broader, easier version of HumanEval — more variety, less difficulty.

**BigCodeBench**
1,140 harder real-world coding tasks involving function calls, libraries, and multi-step logic.
- *ipoefgfefs:* Best measure of real-world code quality. Hardest benchmark in our table. Llama 3.3 70B = ~68%.
- *Real world:* A senior developer's technical interview — real-world tasks, not toy problems.

**MMLU (Massive Multitask Language Understanding)**
57-subject multiple choice exam covering math, science, law, history, medicine, etc.
- *ipoefgfefs:* Measures reasoning ability — important for Pass A (planning block wiring from workflow.json). Phi-4 14B = ~84%.
- *Real world:* A comprehensive university entrance exam across all subjects.

**pass@1**
The metric used in HumanEval — what percentage of problems does the model solve correctly on the very first attempt (no retries).
- *ipoefgfefs:* Higher pass@1 = fewer feedback loop retries needed in ipoefgfefs compile pipeline.
- *Real world:* First-time pass rate on a driver's test — no do-overs counted.

---

## ipoefgfefs Architecture Terms

**custom_logic block**
A variadic block type in ipoefgfefs where the SLM generates the C++ implementation. Inputs wired dynamically from other blocks.
- *ipoefgfefs:* The `match_node` in loitering-face-match workflow — stitches loitering events and face crops from two upstream blocks.
- *Real world:* The glue code between two APIs — written per-use-case, not pre-built.

**pipeline.so**
The compiled shared library that runs on the camera. Output of the entire ipoefgfefs compile chain.
- *ipoefgfefs:* `aarch64-linux-gnu-g++ → libpipeline.so` → hot-reloaded on camera via SIGUSR1.
- *Real world:* A plugin DLL loaded by an application — self-contained, loadable at runtime.

**Two-Pass Generation**
Pass A: SLM generates an IR (intermediate representation / plan). Pass B: SLM generates C++ from that IR.
- *ipoefgfefs:* Pass A = JSON describing block wiring and type map. Pass B = actual C++ `process_frame()` code.
- *Real world:* Architect draws blueprint (Pass A) before the builder starts construction (Pass B).

**IR (Intermediate Representation)**
The structured plan output from Pass A — describes what the code should do before writing the code.
- *ipoefgfefs:* JSON with block connections, data types, event conditions, and output rules.
- *Real world:* An architect's blueprint — describes the building without being the building.

**Compile Gate**
One of 5 validation steps in the ipoefgfefs compile pipeline.
- *ipoefgfefs:* Gate 0=input lint, Gate 1=static checks, Gate 2=cross-compile, Gate 3=smoke test, Gate 4=policy checks.
- *Real world:* CI/CD pipeline stages — each gate must pass before the next runs.

**Feedback Loop**
When a compile gate fails, the error is fed back to the SLM as context for a retry attempt.
- *ipoefgfefs:* Gate 2 fails with `error: 'float' is not 'double'` → error sent back to SLM → SLM retries with fix → up to 6 iterations.
- *Real world:* Code review cycle — reviewer gives feedback, developer fixes, review repeats until approved.

**ONVIF**
IP camera event standard using XML notifications over HTTP.
- *ipoefgfefs:* Loitering events from the Ambarella S50 arrive as ONVIF XML to the pipeline engine.
- *Real world:* Email standard (SMTP) — a common format all cameras speak, like email between different clients.

**MQTT**
Lightweight publish/subscribe messaging protocol for IoT.
- *ipoefgfefs:* Camera publishes events (person detected, loitering triggered) to Mosquitto broker on server. Server subscribes and feeds into ML pipeline.
- *Real world:* WhatsApp group message — camera posts, multiple subscribers receive simultaneously.

**SIGUSR1**
Unix signal sent to a process to trigger custom behavior — used for hot-reload in ipoefgfefs.
- *ipoefgfefs:* After new `pipeline.so` deployed to camera, `kill -SIGUSR1 <pid>` triggers the pipeline engine to reload without reboot.
- *Real world:* `nginx -s reload` — applies config changes without dropping connections.

**Cross-Compile**
Building an executable on one architecture (x86 server) for a different target architecture (aarch64 camera).
- *ipoefgfefs:* Ubuntu server runs `aarch64-linux-gnu-g++` to produce ARM binaries that run on the Ambarella S50.
- *Real world:* Building an Android APK on your Mac — your Mac runs x86, the phone runs ARM.

**Variadic Block**
A block type with dynamically-defined inputs — number and type of inputs depend on what the user wires in the workflow builder.
- *ipoefgfefs:* `custom_logic` block — can receive 2 inputs (loitering + face) or 3 inputs (LPR + face + intrusion) depending on use case.
- *Real world:* A Python `*args` function — accepts any number of arguments.

---

## Compliance & Licensing

**NDAA §889**
Section 889 of the National Defense Authorization Act 2019 — prohibits US government contractors from using telecom/surveillance equipment or services from specific Chinese companies.
- *ipoefgfefs:* Alibaba (Qwen), Huawei, ZTE, Dahua, Hikvision equipment/software cannot be used in products sold to US government. Qwen2.5-coder is BLOCKED.
- *Real world:* Export control law — like not being allowed to sell certain technology to certain countries.

**Apache 2.0**
Open source license — free to use commercially, modify, and distribute. No restriction on use in proprietary products.
- *ipoefgfefs:* Granite 3.3 Code 8B (IBM) and Devstral 24B — can ship in ipoefgfefs product with no fees.
- *Real world:* Using Linux in a commercial product — completely allowed.

**MIT License**
Even more permissive than Apache 2.0 — same freedoms, fewer requirements for attribution.
- *ipoefgfefs:* Phi-4 14B and Phi-3.5-mini 3.8B (Microsoft) — cleanest license possible.
- *Real world:* Using jQuery in a commercial web app.

**Llama Community License**
Meta's custom license for Llama models. Commercial use allowed up to 700M monthly active users.
- *ipoefgfefs:* Llama 3.1 8B and Llama 3.3 70B — allowed for ipoefgfefs (nowhere near 700M users).
- *Real world:* Freemium SaaS — free up to a usage threshold, then you need an enterprise agreement.

**Gemma ToS (Terms of Service)**
Google's restrictive terms for Gemma models — commercial use allowed but with restrictions on competing products and data usage.
- *ipoefgfefs:* Gemma 3 4B and CodeGemma 7B — need ipo legal to review before shipping in product.
- *Real world:* A software EULA with commercial use clauses — generally OK but read the fine print.

**FULL Tier**
Internal compliance classification: US company + US-hosted weights + Apache 2.0 or MIT license.
- *ipoefgfefs:* Phi-4 (Microsoft), Granite 3.3 (IBM), Llama 3.x (Meta) — safest for DoD and federal contracts.
- *Real world:* Made in USA label — highest domestic content guarantee.

**ALLY Tier**
EU or Canada company + open license + no sanctioned country supply chain links.
- *ipoefgfefs:* Devstral 24B (Mistral AI, France), Mistral 7B — safe for most ipo commercial contracts.
- *Real world:* Manufactured in EU — meets most US import standards.

**COMMERCIAL Tier**
Restrictive ToS despite being from a US or EU company — needs legal review before shipping.
- *ipoefgfefs:* Codestral 22B (commercial restriction), Gemma (Google ToS).
- *Real world:* A commercial SDK with a paid license — allowed but read the contract.

**BLOCKED Tier**
China, Russia, Iran, DPRK, or sanctioned entity origin — cannot use in any ipo product.
- *ipoefgfefs:* Qwen (Alibaba), DeepSeek, InternLM (Shanghai AI Lab), Yi-Coder (01.AI).
- *Real world:* Huawei equipment — banned from US government networks by law.

---

## Inference Engines

**llama.cpp**
Open source C++ inference engine for GGUF models. No daemon, embeddable, cross-platform.
- *ipoefgfefs:* The production inference engine for ipoefgfefs compile server. Call via `llama-cpp-python` from Flask API.
- *Real world:* FFmpeg for video — the universal, embeddable tool that just works everywhere.

**llama-cpp-python**
Python bindings for llama.cpp — lets you call the C++ engine from Python without subprocess calls.
- *ipoefgfefs:* `from llama_cpp import Llama; llm = Llama(model_path="...", n_gpu_layers=99)` inside Flask compile API.
- *Real world:* PyOpenCV — Python wrapper around the C++ OpenCV library.

**Ollama**
Wrapper around llama.cpp that adds model management, a REST API, and a daemon process.
- *ipoefgfefs:* Good for POC and testing. Replace with llama-cpp-python for production.
- *Real world:* Docker for models — easy to pull and run, but adds overhead vs running the binary directly.

**vLLM**
High-throughput GPU inference engine with paged KV cache for concurrent requests.
- *ipoefgfefs:* Not needed now (small team). Add when 10+ users compile simultaneously.
- *Real world:* A web server with connection pooling — handles many users at once, overkill for a personal site.

**SGLang**
Stanford's inference engine with RadixAttention — caches shared prompt prefixes across requests.
- *ipoefgfefs:* Best engine when ipoefgfefs scales to a team, because every compile prompt shares the same 6K-token header prefix.
- *Real world:* A library that caches the card catalogue — repeated searches on same author are instant.

**FIM (Fill-In-the-Middle)**
Model capability to generate code between a given prefix and suffix.
- *ipoefgfefs:* Not used in current ipoefgfefs (we generate whole functions). Codestral, CodeLlama, Granite, Starcoder2 support it.
- *Real world:* IDE autocomplete that fills a gap mid-function — type the start and end, AI fills the middle.

**Chat Template**
The prompt format a model expects — wraps your message in special tokens the model was trained with.
- *ipoefgfefs:* Devstral needs `mistral` template. Phi-4 needs `phi3`. Wrong template = model ignores instructions. Set with `--chat-template mistral` in llama.cpp.
- *Real world:* Email format — Subject line, To, Body in the right fields. Wrong format = message ignored.

**GQA (Grouped Query Attention)**
Attention variant where multiple query heads share the same key/value head — reduces KV cache memory.
- *ipoefgfefs:* Llama 3.x and Mistral 7B use GQA — their KV cache is smaller, fits more context in same VRAM.
- *Real world:* Shared meeting notes — multiple people reading the same notes instead of each keeping a copy.

**MoE (Mixture of Experts)**
Architecture where only a subset of the model's parameters are active for each token — more params, same compute cost.
- *ipoefgfefs:* Devstral Small uses MoE-style routing — 24B total params but only ~8B active per token. That's why it's efficient.
- *Real world:* A hospital with 10 specialist departments — each patient sees only the relevant specialist, not all 10.

**Tokenizer**
Algorithm that splits text into tokens (subword units) before feeding to the model.
- *ipoefgfefs:* Devstral uses SentencePiece, Llama 3.x uses tiktoken. Matters for accurate token counting in `gen_slm_prompt.py`.
- *Real world:* A word processor's spell checker that splits text into recognized chunks before checking.

**BPE (Byte Pair Encoding)**
The most common tokenization algorithm — merges frequent character pairs into tokens.
- *ipoefgfefs:* Llama 3.x, Phi models use BPE-based tokenizers (tiktoken). 1 token ≈ 0.75 words in English, less in code.
- *Real world:* Compression algorithm — frequently seen patterns get shorter codes.

**Hallucination**
When a model generates plausible-sounding but incorrect output — invents a function that doesn't exist.
- *ipoefgfefs:* SLM generates `cv::faceMatch(crop, template)` — a function that doesn't exist in OpenCV. Gate 2 catches this.
- *Real world:* GPS giving directions to a road that was demolished 5 years ago.
