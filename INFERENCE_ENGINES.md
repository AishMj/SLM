# Inference Engine Comparison — snorkelbadger SLM Deploy

Which engine to use at each stage of snorkelbadger development.

---

## Quick Decision

| Stage | Engine | Why |
|---|---|---|
| Day 1 POC | Ollama | Zero setup, `ollama pull devstral` and done |
| Production server | llama-cpp-python | Embed in Flask, GPU via `n_gpu_layers=99`, no daemon |
| Team of 10+ users | SGLang | Prefix caching kills TTFT on repeated prompts |
| A100 server (future) | vLLM or NIM | Highest throughput, paged KV cache |
| Demo to manager | llamafile | Single file, runs anywhere without installation |

---

## Full Comparison Table

| Engine | ARM A53 | Prod Ready | snorkelbadger Fit | Main Advantage | Main Limitation | POC → Prod Path |
|---|---|---|---|---|---|---|
| **llama.cpp** | Yes | Yes | ★★★★★ | No daemon, GGUF, C++ embeddable, GPU via `-ngl 99` | One request at a time | Start and stay here for server SLM |
| **llama-cpp-python** | Yes | Yes | ★★★★★ | Direct Python import inside Flask, no subprocess | Binds to llama.cpp version | Use this in prod Flask API |
| **Ollama** | No | POC only | ★★★ POC | Dead simple, auto-downloads GGUF | Daemon, extra HTTP hop, harder to embed | POC only, replace with llama-cpp-python |
| **SGLang** | No | Yes | ★★★★★ scale | RadixAttention — caches shared 6K-token header prefix | Python server, CUDA preferred | Switch from llama.cpp when team grows |
| **vLLM** | No | Yes | ★★★ GPU | Highest throughput, paged KV cache, concurrent requests | CUDA-only, Python server, overkill for small team | Add when 20+ concurrent compile requests |
| **TGI** | No | Yes | ★★★ | HuggingFace native, Docker image, REST API | Heavy setup, CUDA preferred | Alternative to vLLM if HF ecosystem preferred |
| **ExLlamaV2** | No | Partial | ★★ RTX | Fastest GPTQ on RTX 30xx/40xx series | Python, CUDA only | If server gets RTX and you want max speed |
| **TabbyAPI** | No | Partial | ★★★ | ExLlamaV2 with OpenAI-compatible REST API | Limited model support | Middle ground between Ollama and vLLM |
| **TensorRT-LLM** | No | Enterprise | ★★ future | Fastest on A100/H100, NVIDIA optimized | Complex build, NVIDIA only | Future if Honeywell provides A100 infra |
| **NVIDIA NIM** | No | Enterprise | ★★★ future | TRT-LLM packaged as Docker container, managed | Paid NGC subscription, NVIDIA only | If ipo gets NVIDIA enterprise contract |
| **MLC-LLM** | Some | Partial | ★ edge | Compiles model to target CPU/GPU | Limited model support | Future edge SLM on camera |
| **ONNX Runtime** | Phi only | Partial | ★ Phi only | Wide hardware, Phi-3.5-mini edge path | Only few models, no GGUF | Phi-3.5-mini ARM camera path only |
| **CTranslate2** | No | Partial | ★★ CPU | Fastest CPU inference, 20-30% faster than llama.cpp | No GGUF, separate conversion step | If server has no GPU |
| **Groq (cloud)** | No | Dev only | ★★★ demos | 800+ tok/s on cloud hardware | Data leaves server (privacy risk), not self-hosted | POC/demos only, not prod |
| **llamafile** | No | Dev | ★★★ demos | Single file, runs on any OS without install | Not embeddable, not for server deployment | Demo to managers or field engineers |
| **MLX** | No | Dev only | No | Fast on Apple Silicon | macOS only — server is Ubuntu | Not applicable |

---

## Why SGLang Matters for snorkelbadger Specifically

Every snorkelbadger compile prompt starts with the **same 6,000–8,000 tokens**:
- System instructions
- C++ block header files
- workflow_blocks.json schema
- Compile constraints

With llama.cpp or vLLM, the model re-reads all 8K tokens every single request. At 8K tokens on Devstral 24B CPU, that takes 3–5 seconds before the first C++ token appears.

SGLang's RadixAttention caches this shared prefix after the first request. All future requests get a cache hit — TTFT drops from 3–5s to ~0.2s.

```
Without SGLang (llama.cpp):
  Request 1: read 8K prefix (4s) + generate 400 tokens (13s) = 17s total
  Request 2: read 8K prefix (4s) + generate 400 tokens (13s) = 17s total
  Request 3: read 8K prefix (4s) + generate 400 tokens (13s) = 17s total

With SGLang:
  Request 1: read 8K prefix (4s) + generate 400 tokens (13s) = 17s total
  Request 2: cache hit (0.2s) + generate 400 tokens (13s) = 13.2s total
  Request 3: cache hit (0.2s) + generate 400 tokens (13s) = 13.2s total
```

22% faster per request for every request after the first. For a team of 5 compiling 20 times a day = 100 requests. 99 of them benefit from caching. Significant.

---

## llama-cpp-python Integration (Production Pattern)

```python
from llama_cpp import Llama

# Load once at server startup, not per request
llm = Llama(
    model_path="/models/devstral-small-24b-Q4_K_M.gguf",
    n_gpu_layers=99,      # offload all layers to GPU
    n_ctx=16384,          # context window (prompt + output)
    n_threads=8,          # CPU threads for non-GPU layers
    verbose=False
)

def generate_cpp(prompt: str) -> str:
    response = llm(
        prompt=prompt,
        max_tokens=800,       # enough for a C++ method
        temperature=0.1,      # low = deterministic, good for code
        stop=["```", "//END"] # stop tokens
    )
    return response["choices"][0]["text"]
```

Key points:
- Load `llm` once at Flask startup, reuse for every request
- `n_gpu_layers=99` = put all model layers on GPU (use 0 for CPU-only)
- `temperature=0.1` = near-deterministic output (important for code)
- `n_ctx=16384` = enough for 8K prompt + 800 token output
