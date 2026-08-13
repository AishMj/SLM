# llama.cpp - setup and running the models

Everything needed to go from a bare Ubuntu box to serving a GGUF model for the
ipoefgfefs workflow builder. Written against an NVIDIA A30 24 GB, but the only
thing that changes for another card is the CUDA architecture number in step 2.

---

## Contents

1. [What llama.cpp is](#1-what-llamacpp-is)
2. [Build it](#2-build-it)
3. [Get the models](#3-get-the-models)
4. [Run a model](#4-run-a-model)
5. [Run it as a server](#5-run-it-as-a-server)
6. [The flags that matter](#6-the-flags-that-matter)
7. [Speculative decoding - free speedup](#7-speculative-decoding---free-speedup)
8. [Benchmarking](#8-benchmarking)
9. [Calling it from Python](#9-calling-it-from-python)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. What llama.cpp is

A C++ inference engine that runs language models from a single `.gguf` file.
No Python, no PyTorch, no CUDA toolkit at runtime, no model directory - one file
in, tokens out.

Why we use it:

- runs on CPU, NVIDIA, AMD and Apple, and on aarch64 for the camera
- GGUF is self-contained, so deployment is a file copy
- quantized models load in seconds and use a quarter of the memory
- it ships a server with an OpenAI-compatible API, so the Flask layer barely changes

**Trade-off:** it is optimised for one request at a time. If several engineers hit
the builder simultaneously, look at SGLang or vLLM instead. For now, single-request
latency is what matters and llama.cpp wins on that.

---

## 2. Build it

### Prerequisites

```bash
sudo apt update
sudo apt install -y build-essential cmake git libcurl4-openssl-dev
```

For GPU you need the CUDA toolkit. Check it is there:

```bash
nvcc --version
nvidia-smi
```

If `nvcc` is missing, install the toolkit that matches the driver reported by
`nvidia-smi`. Do not install a newer toolkit than the driver supports.

### Clone and build

```bash
cd /opt
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp

# CUDA build. 80 = Ampere, which covers the A30 and A100.
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=80

cmake --build build --config Release -j $(nproc)
```

Build takes about 5-10 minutes.

**CUDA architecture by card:**

| Card | Architecture flag |
|---|---|
| A30, A100, RTX 30xx | `80` |
| RTX 40xx, L40S | `89` |
| H100 | `90` |
| RTX 50xx / Blackwell | `120` |
| Leave it out | builds for all, much slower to compile |

### CPU-only build

If there is no GPU on the box:

```bash
cmake -B build
cmake --build build --config Release -j $(nproc)
```

### Check it worked

```bash
./build/bin/llama-cli --version
```

Binaries land in `build/bin/`. The ones we use are `llama-cli`, `llama-server`
and `llama-bench`. Put them on PATH if you like:

```bash
echo 'export PATH=$PATH:/opt/llama.cpp/build/bin' >> ~/.bashrc
source ~/.bashrc
```

---

## 3. Get the models

Models are GGUF files. Download on any machine, copy to the server - there is
nothing else to install.

```bash
mkdir -p /opt/models
```

### Download directly on the server

```bash
pip install huggingface_hub

huggingface-cli download Qwen/Qwen2.5-Coder-7B-Instruct-GGUF \
  qwen2.5-coder-7b-instruct-q4_k_m.gguf --local-dir /opt/models
```

### Or copy from a Windows machine

```bash
scp user@windows-box:/d/models/*.gguf /opt/models/
```

### Always verify after transfer

A truncated GGUF fails in confusing ways - usually a tokenizer error that looks
like a model problem.

```bash
sha256sum /opt/models/*.gguf
```

Compare against the hash shown on the file's HuggingFace page.

### The models we use

| Model | File | Size | Role |
|---|---|---|---|
| Qwen2.5-Coder 7B | `qwen2.5-coder-7b-instruct-q4_k_m.gguf` | 4.68 GB | Primary C++ generator |
| Granite 3.3 8B | `granite-3.3-8b-instruct-Q4_K_M.gguf` | 4.94 GB | Alternative, US-origin |
| CodeGemma 7B | `codegemma-7b-it-Q4_K_M.gguf` | ~5.1 GB | Comparison only - 8K context |
| Qwen2.5-Coder 1.5B | `qwen2.5-coder-1.5b-instruct-q4_k_m.gguf` | 1.12 GB | Draft model, see section 7 |
| Phi-3.5-mini | `Phi-3.5-mini-instruct-Q4_K_M.gguf` | ~2.4 GB | Pass A reasoning |
| Qwen2-VL 7B | `qwen2-vl-7b-instruct-q4_k_m.gguf` | ~4.6 GB | Image to text |

**Note the casing.** Qwen publishes lowercase `q4_k_m`, IBM publishes uppercase
`Q4_K_M`. Tab-complete rather than typing it out.

**Note on CodeGemma.** Google's own GGUF repo has no Q4_K_M - only f16 at 16 GB.
Use `bartowski/codegemma-7b-it-GGUF` instead.

---

## 4. Run a model

### One-shot prompt

```bash
llama-cli -m /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  -p "Write a C++14 function that returns the maximum value in a std::vector<int>." \
  -n 256 \
  -ngl 99 \
  -c 16384 \
  --temp 0.2
```

### Interactive chat

```bash
llama-cli -m /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  -ngl 99 -c 16384 -cnv
```

`-cnv` puts it in conversation mode and applies the model's chat template
automatically. Ctrl-C to exit.

### Read the prompt from a file

Useful for the real 6-8K ipoefgfefs prompt:

```bash
llama-cli -m /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  -f prompts/custom_logic_prompt.txt \
  -n 512 -ngl 99 -c 16384 --temp 0.2
```

---

## 5. Run it as a server

This is what the Flask layer talks to.

```bash
llama-server \
  -m /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  -ngl 99 \
  -c 16384 \
  --host 0.0.0.0 \
  --port 8080 \
  --parallel 2
```

The API is OpenAI-compatible, so any OpenAI client library works against it.

### Test it

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Write a C++14 function to clamp an int between two bounds."}
    ],
    "temperature": 0.2,
    "max_tokens": 256
  }'
```

There is also a browser UI at `http://<server>:8080` for quick manual testing.

### Run it as a service

```bash
sudo tee /etc/systemd/system/llama-server.service > /dev/null <<'EOF'
[Unit]
Description=llama.cpp server for ipoefgfefs
After=network.target

[Service]
Type=simple
User=ipoefgfefs
ExecStart=/opt/llama.cpp/build/bin/llama-server \
  -m /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  -ngl 99 -c 16384 --host 127.0.0.1 --port 8080 --parallel 2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now llama-server
sudo systemctl status llama-server
```

Bind to `127.0.0.1` if only the local Flask app talks to it. Use `0.0.0.0` only
if something on another host needs it, and put it behind a firewall.

---

## 6. The flags that matter

| Flag | What it does | What we use |
|---|---|---|
| `-m` | Path to the .gguf file | required |
| `-ngl N` | Layers to offload to GPU. 99 means all of them. | `99` |
| `-c N` | Context size in tokens | `16384` |
| `-n N` | Max tokens to generate | `512` for a block |
| `--temp` | Randomness. 0 is deterministic. | `0.2` for code |
| `--top-p` | Nucleus sampling cutoff | `0.95` |
| `-t N` | CPU threads. Only matters without a GPU. | `$(nproc)` |
| `--parallel N` | Concurrent slots on the server | `2` |
| `-s N` | Random seed. Fix it for reproducible evals. | `42` |
| `-f FILE` | Read the prompt from a file | for long prompts |
| `-cnv` | Conversation mode with chat template | interactive only |

### Why `-c 16384`

The ipoefgfefs prompt is 6-8K tokens. 16K gives room for the prompt plus a
generated block, with headroom.

Do not set it to the model's advertised maximum. The KV cache grows linearly with
context, and it is allocated up front:

```
Qwen2.5-Coder 7B at  16K ctx  ->   5.2 GB total
Qwen2.5-Coder 7B at 131K ctx  ->  11.3 GB total
Granite 3.3 8B   at 131K ctx  ->  24.5 GB total  - does not fit a 24 GB card
```

Set the context you actually need. Setting it high "just in case" wastes VRAM and
can push a model off the card entirely.

### Why `--temp 0.2`

Code generation wants near-deterministic output. Temperature 0 can loop on
repetitive text, so 0.2 is the usual compromise. For the compile-retry evaluation
set `-s 42` as well, so runs are comparable.

---

## 7. Speculative decoding - free speedup

A small model proposes tokens, the big model verifies them in one batched pass.
**The output is identical** to running the big model alone - it is lossless by
construction - but typically 1.5-2x faster.

```bash
llama-server \
  -m  /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  -md /opt/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf \
  -ngl 99 -ngld 99 \
  -c 16384 --host 0.0.0.0 --port 8080
```

`-md` is the draft model, `-ngld` offloads its layers to GPU too.

**The draft model must share a tokenizer with the target.** Qwen2.5-Coder 1.5B
with Qwen2.5-Coder 7B works. Mixing families does not.

Costs 1.12 GB of VRAM. For a loop that can run six compile-retry iterations, that
is a good trade.

---

## 8. Benchmarking

```bash
llama-bench -m /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf
```

Reports two numbers:

- **pp** - prompt processing, tokens/sec reading the prompt
- **tg** - text generation, tokens/sec writing the answer

`tg` is the one people mean by "tokens per second".

### Benchmark at our real prompt size

Default is 512 tokens, which flatters the result. Use something realistic:

```bash
llama-bench -m /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  -p 8192 -n 512 -ngl 99
```

Expect roughly 20-25% lower `tg` than the 512-token default. That is normal - the
KV cache is larger, so each token costs more memory traffic.

### Compare all candidates

```bash
for f in /opt/models/*q4_k_m*.gguf /opt/models/*Q4_K_M*.gguf; do
  echo "=== $f"
  llama-bench -m "$f" -p 8192 -n 256 -ngl 99
done
```

### Sanity check against the estimate

Our sizing model predicts:

```
tok/s = card_bandwidth_GBs x 0.59 / model_size_GB
```

For an A30 at 933 GB/s with the 4.68 GB Qwen file, that is about **118 tok/s**.
If `llama-bench` lands within ~15% of that, the model is calibrated for this box.
If it is well off, re-solve for the real efficiency:

```
efficiency = measured_tok_per_sec x model_size_GB / 933
```

---

## 9. Calling it from Python

Two options.

### Option A - talk to llama-server over HTTP (recommended)

Keeps inference in a separate process, so a model crash does not take down Flask,
and the model can be swapped without restarting the app.

```python
import requests

LLAMA_URL = "http://127.0.0.1:8080/v1/chat/completions"


def generate_custom_logic(prompt, max_tokens=512):
    # temperature is low on purpose - we want repeatable C++, not creative C++
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "top_p": 0.95,
        "max_tokens": max_tokens,
        "seed": 42,
    }
    r = requests.post(LLAMA_URL, json=payload, timeout=300)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
```

### Option B - embed it in the process

```bash
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
```

```python
from llama_cpp import Llama

llm = Llama(
    model_path="/opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf",
    n_gpu_layers=-1,   # -1 means all layers on GPU
    n_ctx=16384,
    seed=42,
    verbose=False,
)

out = llm.create_chat_completion(
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    max_tokens=512,
)
print(out["choices"][0]["message"]["content"])
```

Lower latency, but the model lives inside the Flask worker - so every worker loads
its own copy of the weights. With multiple workers that multiplies VRAM. Prefer
Option A unless you have measured a reason not to.

---

## 10. Troubleshooting

**`CUDA error: out of memory`**
Context is too large or `-ngl` is too high. Drop `-c` first - the KV cache is
usually the culprit, not the weights. Check with `nvidia-smi` while it loads.

**Model loads but runs on CPU (very slow)**
`-ngl` was not set, or the build has no CUDA. Confirm with:
```bash
llama-cli --version   # should mention CUDA
ldd build/bin/llama-cli | grep cuda
```

**`failed to load model` / tokenizer errors**
Usually a truncated download. Re-check `sha256sum` against HuggingFace.

**Gibberish output**
Wrong chat template. Use `-cnv` with `llama-cli`, or the `/v1/chat/completions`
endpoint rather than `/completion`, so the template is applied.

**Output stops mid-function**
`-n` is too low. A custom_logic block needs about 512 tokens.

**Slower than expected**
Check the GPU is actually being used:
```bash
watch -n 0.5 nvidia-smi
```
Utilisation should sit high during generation. If it is near zero, layers are not
offloaded.

**`nvcc` and driver mismatch at build time**
The CUDA toolkit is newer than the driver supports. Either update the driver or
install a toolkit matching `nvidia-smi`.

---

## Quick reference

```bash
# build
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=80
cmake --build build --config Release -j $(nproc)

# one-shot
llama-cli -m model.gguf -p "prompt" -n 512 -ngl 99 -c 16384 --temp 0.2

# server
llama-server -m model.gguf -ngl 99 -c 16384 --host 0.0.0.0 --port 8080

# server with draft model
llama-server -m big.gguf -md small.gguf -ngl 99 -ngld 99 -c 16384

# benchmark at a realistic prompt size
llama-bench -m model.gguf -p 8192 -n 256 -ngl 99

# verify a download
sha256sum model.gguf
```

---

## References

| What | Where |
|---|---|
| llama.cpp repository | https://github.com/ggml-org/llama.cpp |
| Build documentation | https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md |
| Server documentation | https://github.com/ggml-org/llama.cpp/tree/master/tools/server |
| llama-cpp-python | https://github.com/abetlen/llama-cpp-python |
| GGUF format spec | https://github.com/ggml-org/ggml/blob/master/docs/gguf.md |
| Model sizing and VRAM maths | `ipoefgfefs_SLM_Matrix.xlsx`, Detailed sheet |
