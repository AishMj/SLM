# Model downloads - the ipoefgfefs stack

The models we selected, where to get them, and the exact filenames.
Not a catalogue - only what we intend to run.

Setup and usage: [LLAMA_CPP_SETUP.md](LLAMA_CPP_SETUP.md)
Selection rationale and benchmarks: `ipoefgfefs_SLM_Matrix.xlsx`

Target hardware: NVIDIA A30 24 GB, Ubuntu, llama.cpp.
All Q4_K_M, which is what we deploy.

---

## The stack

| Role | Model | Q4_K_M | VRAM @16K ctx |
|---|---|---|---|
| C++ generation - primary | Qwen2.5-Coder 7B | 4.68 GB | 5.2 GB |
| C++ generation - alternative | Granite 3.3 8B | 4.94 GB | 7.0 GB |
| C++ generation - comparison | CodeGemma 7B | ~5.1 GB | 8.3 GB |
| Pass A reasoning | Phi-3.5-mini 3.8B | ~2.4 GB | 8.1 GB |
| Image to text / LPR | Qwen2-VL 7B | ~4.6 GB | 5.5 GB |
| Image + video embeddings | Qwen3-VL-Embedding-8B | 16 GB FP16 | 19.2 GB |
| Draft model - speedup | Qwen2.5-Coder 1.5B | 1.12 GB | 1.3 GB |

Running one code model plus one vision model at a time is about 10 GB.
Everything fits the 24 GB card with room for fine-tuning.

---

## Two things that will waste your time

**1. Filename casing differs by publisher.**

```
Qwen ships lowercase :  qwen2.5-coder-7b-instruct-q4_k_m.gguf
IBM  ships uppercase :  granite-3.3-8b-instruct-Q4_K_M.gguf
```

Tab-complete rather than typing. A 404 on a scripted download is usually this.

**2. Google's official CodeGemma GGUF repo has no Q4_K_M.**

`google/codegemma-7b-it-GGUF` holds only an f16 at 16.2 GB and an unquantized
34.2 GB file. Use the `bartowski` conversion instead.

---

## Download URLs

### Code generation

| Model | Repo | Filename | Size |
|---|---|---|---|
| **Qwen2.5-Coder 7B** | [Qwen/Qwen2.5-Coder-7B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF) | `qwen2.5-coder-7b-instruct-q4_k_m.gguf` | **4.68 GB** verified |
| **Granite 3.3 8B** | [ibm-granite/granite-3.3-8b-instruct-GGUF](https://huggingface.co/ibm-granite/granite-3.3-8b-instruct-GGUF) | `granite-3.3-8b-instruct-Q4_K_M.gguf` | **4.94 GB** verified |
| **CodeGemma 7B-it** | [bartowski/codegemma-7b-it-GGUF](https://huggingface.co/bartowski/codegemma-7b-it-GGUF) | `codegemma-7b-it-Q4_K_M.gguf` | ~5.1 GB |

### Reasoning - Pass A

| Model | Repo | Filename | Size |
|---|---|---|---|
| **Phi-3.5-mini** | [bartowski/Phi-3.5-mini-instruct-GGUF](https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF) | `Phi-3.5-mini-instruct-Q4_K_M.gguf` | ~2.4 GB |

### Vision - image to text and licence plates

| Model | Repo | Filename | Size |
|---|---|---|---|
| **Qwen2-VL 7B** | [bartowski/Qwen2-VL-7B-Instruct-GGUF](https://huggingface.co/bartowski/Qwen2-VL-7B-Instruct-GGUF) | `Qwen2-VL-7B-Instruct-Q4_K_M.gguf` | ~4.6 GB |
| | | `mmproj-Qwen2-VL-7B-Instruct-f16.gguf` | ~1.4 GB |

**Vision needs two files** - the language weights plus an `mmproj` projector that
encodes the image. Pass the projector with `--mmproj`. Vision support in
llama.cpp lags the text path, so check the current state before depending on it.

### Draft model - speculative decoding

| Model | Repo | Filename | Size |
|---|---|---|---|
| **Qwen2.5-Coder 1.5B** | [Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF) | `qwen2.5-coder-1.5b-instruct-q4_k_m.gguf` | **1.12 GB** verified |

### Embeddings - NOT llama.cpp

| Model | Repo | Note |
|---|---|---|
| Qwen3-VL-Embedding-8B | [Qwen/Qwen3-VL-Embedding-8B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B) | full repo, FP16 |
| Qwen3-VL-Embedding-2B | [Qwen/Qwen3-VL-Embedding-2B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B) | full repo, FP16 |

**No GGUF exists for these.** They run under transformers or vLLM in embedding
mode - a second serving path alongside llama.cpp. Clone the whole repo, not a
single file.

**Consider the 2B instead of the 8B.** It scores 75.0 against 80.1 on MMEB-V2
Image but needs 4.8 GB instead of 19.2 GB. Five points for fifteen gigabytes.
If embeddings run alongside code generation, the 2B is the practical choice.

---

## Lightweight code models - under 4B

For the camera, for low-VRAM boxes, and as draft models. All of these fit in
under 2 GB at Q4_K_M, and the small Qwen variants are far stronger than their
size suggests.

Scores below are from the Qwen2.5-Coder technical report, arxiv 2409.12186 -
HumanEval and MBPP from Table 16, MultiPL-E C++ from Table 17. StarCoder2 C++
is from arxiv 2402.19173 Table 10.

| Model | Params | Q4_K_M | MultiPL-E C++ | HumanEval | Repo | Filename |
|---|---|---|---|---|---|---|
| **Qwen2.5-Coder 3B** | 3B | ~1.9 GB | **68.3%** | **84.1%** | [Qwen/Qwen2.5-Coder-3B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF) | `qwen2.5-coder-3b-instruct-q4_k_m.gguf` |
| **Qwen2.5-Coder 1.5B** | 1.5B | **1.12 GB** | **50.9%** | 70.7% | [Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF) | `qwen2.5-coder-1.5b-instruct-q4_k_m.gguf` |
| **Qwen2.5-Coder 0.5B** | 0.5B | ~0.4 GB | 43.5% | 61.6% | [Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF) | `qwen2.5-coder-0.5b-instruct-q4_k_m.gguf` |
| Granite 3.3 2B | 2B | ~1.5 GB | not published | not published | [ibm-granite/granite-3.3-2b-instruct-GGUF](https://huggingface.co/ibm-granite/granite-3.3-2b-instruct-GGUF) | `granite-3.3-2b-instruct-Q4_K_M.gguf` |
| CodeGemma 2B | 2B | ~1.6 GB | not published | completion only | [bartowski/codegemma-2b-GGUF](https://huggingface.co/bartowski/codegemma-2b-GGUF) | `codegemma-2b-Q4_K_M.gguf` |
| DeepSeek-Coder 1.3B | 1.3B | ~0.8 GB | not published | not published | [bartowski/deepseek-coder-1.3b-instruct-GGUF](https://huggingface.co/bartowski/deepseek-coder-1.3b-instruct-GGUF) | `deepseek-coder-1.3b-instruct-Q4_K_M.gguf` |
| StarCoder2 3B | 3B | ~1.7 GB | 27.2% | 31.7% | [bartowski/starcoder2-3b-GGUF](https://huggingface.co/bartowski/starcoder2-3b-GGUF) | `starcoder2-3b-Q4_K_M.gguf` |

### The finding worth acting on

Put the small Qwen variants against the big models we evaluated:

```
Qwen2.5-Coder  3B  at  1.9 GB   ->  C++ 68.3%
Qwen2.5-Coder  7B  at  4.7 GB   ->  C++ 75.6%
StarCoder2    15B  at  9.0 GB   ->  C++ 41.4%
CodeGemma      7B  at  5.1 GB   ->  C++ 42.2%  (BabelCode, not directly comparable)
```

**Qwen2.5-Coder 3B reaches 90% of the 7B's C++ score at 40% of the size**, and it
beats StarCoder2 15B by 27 points while being a fifth of the footprint. Even the
1.5B at 1.1 GB outscores StarCoder2 15B on C++.

Two consequences:

- **The camera is not out of reach for real code generation.** At 1.9 GB the 3B
  fits the Ambarella S50 budget. Nothing else in this class comes close on C++.
- **The 3B is a serious fallback for the server**, not just a toy. If throughput
  ever matters more than the last few points of accuracy, it runs roughly 2.5x
  faster than the 7B for a 7-point C++ drop.

### Which one to take

| Use | Model | Why |
|---|---|---|
| Edge / camera code generation | Qwen2.5-Coder 3B | Best C++ that fits ~2 GB |
| Draft model for the 7B | Qwen2.5-Coder 1.5B | Same tokenizer, 1.1 GB, lossless speedup |
| Smoke tests, CI, laptops | Qwen2.5-Coder 0.5B | 0.4 GB, still 43.5% C++ |
| Avoid for C++ | StarCoder2 3B | 27.2% C++, and the family has a documented FIM bug |

```bash
# the lightweight set, about 3.4 GB total
for M in 0.5B 1.5B 3B; do
  L=$(echo $M | tr 'A-Z' 'a-z')
  huggingface-cli download Qwen/Qwen2.5-Coder-${M}-Instruct-GGUF \
    qwen2.5-coder-${L}-instruct-q4_k_m.gguf --local-dir /opt/models
done
```

---

## Fallbacks, if the shortlist underperforms

| Model | Repo | Filename | When |
|---|---|---|---|
| Qwen2.5-Coder 14B | [Qwen/Qwen2.5-Coder-14B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF) | `qwen2.5-coder-14b-instruct-q4_k_m.gguf` | If the 7B fails the compile-retry eval. ~9 GB, still fits |
| Qwen2.5-Coder 3B | [Qwen/Qwen2.5-Coder-3B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF) | `qwen2.5-coder-3b-instruct-q4_k_m.gguf` | Edge / camera testing. ~1.9 GB |
| Granite 3.3 2B | [ibm-granite/granite-3.3-2b-instruct-GGUF](https://huggingface.co/ibm-granite/granite-3.3-2b-instruct-GGUF) | `granite-3.3-2b-instruct-Q4_K_M.gguf` | Small US-origin option. ~1.5 GB |

Moving up or down stays inside the same family, so no re-evaluation is needed -
same tokenizer, same prompt format, same behaviour.

---

## Download script

```bash
#!/usr/bin/env bash
# fetch the ipoefgfefs model stack. about 23 GB total.
set -e

DEST=/opt/models
mkdir -p "$DEST"

pip install -q huggingface_hub

echo "[1/6] Qwen2.5-Coder 7B - primary C++ generator"
huggingface-cli download Qwen/Qwen2.5-Coder-7B-Instruct-GGUF \
  qwen2.5-coder-7b-instruct-q4_k_m.gguf --local-dir "$DEST"

echo "[2/6] Qwen2.5-Coder 1.5B - draft model"
huggingface-cli download Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF \
  qwen2.5-coder-1.5b-instruct-q4_k_m.gguf --local-dir "$DEST"

echo "[3/6] Granite 3.3 8B - alternative C++ generator"
huggingface-cli download ibm-granite/granite-3.3-8b-instruct-GGUF \
  granite-3.3-8b-instruct-Q4_K_M.gguf --local-dir "$DEST"

echo "[4/6] CodeGemma 7B - comparison"
huggingface-cli download bartowski/codegemma-7b-it-GGUF \
  codegemma-7b-it-Q4_K_M.gguf --local-dir "$DEST"

echo "[5/6] Phi-3.5-mini - Pass A reasoning"
huggingface-cli download bartowski/Phi-3.5-mini-instruct-GGUF \
  Phi-3.5-mini-instruct-Q4_K_M.gguf --local-dir "$DEST"

echo "[6/6] Qwen2-VL 7B - vision, needs the projector too"
huggingface-cli download bartowski/Qwen2-VL-7B-Instruct-GGUF \
  --include "*Q4_K_M*" --include "*mmproj*" --local-dir "$DEST"

echo
echo "done. verify with:"
echo "  sha256sum $DEST/*.gguf"
ls -lh "$DEST"
```

### If a filename 404s

Case-insensitive wildcard, works whatever the publisher used:

```bash
huggingface-cli download <repo> --include "*[Qq]4_[Kk]_[Mm]*" --local-dir /opt/models
```

### Downloading on Windows, then transferring

```powershell
huggingface-cli download Qwen/Qwen2.5-Coder-7B-Instruct-GGUF `
  qwen2.5-coder-7b-instruct-q4_k_m.gguf --local-dir D:\models
```

```bash
scp /d/models/*.gguf user@ubuntu-box:/opt/models/
sha256sum /opt/models/*.gguf   # compare against the HuggingFace file page
```

Always verify after a transfer. A truncated GGUF fails with a tokenizer error
that looks like a model problem, and you will lose an hour to it.

---

## Order to download

| | Models | Size | Why |
|---|---|---|---|
| **First** | Qwen2.5-Coder 7B, Granite 3.3 8B, CodeGemma 7B | ~15 GB | The three-way compile-retry evaluation |
| **Second** | Qwen2.5-Coder 1.5B | 1.1 GB | Draft model - 1.5-2x speedup, lossless |
| **Third** | Phi-3.5-mini, Qwen2-VL 7B | ~7 GB | Pass A and vision, once codegen is settled |
| **Later** | Qwen3-VL-Embedding | 4.8 or 16 GB | Only if re-ID is in scope for MVP-1 |

---

## Why the 1.5B draft model is worth 1.1 GB

Same tokenizer family as the 7B, so llama.cpp can use it for speculative decoding:

```bash
llama-server -m  /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
             -md /opt/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf \
             -ngl 99 -ngld 99 -c 16384
```

The small model proposes tokens, the 7B verifies them in one batched pass.
**Output is identical** - lossless by construction - but typically 1.5-2x faster.
Across a six-iteration compile-retry loop that is real time saved.

---

## Quantization choice

Q4_K_M unless there is a reason. On 24 GB there is room for Q8 on the 7-8B
models, worth considering for code generation where one wrong token breaks the
compile.

| Quant | Bits/param | Qwen 7.6B | Quality cost |
|---|---|---|---|
| Q4_K_M | 4.5 | 4.3 GB | ~1.5% perplexity |
| Q5_K_M | 5.5 | 5.2 GB | ~0.6% |
| Q8_0 | 8.5 | 8.1 GB | ~0.04% |

`size_GB = params_B x bits / 8`. Add the KV cache for VRAM - see
LLAMA_CPP_SETUP.md section 6.
