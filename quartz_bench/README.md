# quartz_bench

Generate a custom analytic with a small language model, compile it, **run it**,
and check the result against a known answer.

One workflow file per A->B pair. Nothing is hand-written per run - the prompt is
assembled from the workflow.

## Layout

```
common/
  contract.hpp        types + the 4-function allow-list
  helpers.cpp         allow-list implementations + JSON loading
  main.cpp            fixed harness. picks the 1-frame or 2-frame signature
  nlohmann/json.hpp   vendored, so this builds on a bare box
  templates/          one skeleton per block, each ending mid-function

ws_cur/
  workflows/          one .json per A->B pair. THE input.
  testdata/           frames + config, each config carries expected_events
  build_prompt.py     workflow.json -> prompt
  run.sh              generate -> compile -> RUN -> PASS/FAIL
  run_all.sh          every workflow, tabulated
  out/                generated kernels and binaries (gitignored)
```

## Get it and run it

```bash
# download just this folder
git clone --filter=blob:none --no-checkout https://github.com/AishMj/SLM.git qb
cd qb && git sparse-checkout init --cone && git sparse-checkout set quartz_bench
git checkout main && cd quartz_bench

# run
cd ws_cur
./run.sh workflows/wf_intrusion.json
```

`run.sh` finds `llama-cli` and a `.gguf` automatically. It looks on PATH, then
`~/llama.cpp/build/bin`, `/opt/llama.cpp/build/bin`, and two levels up. Models
are looked for in `~/models`, `/opt/models`, `./models`, `../models`.

If it cannot find them:

```bash
export LLAMA=/path/to/llama.cpp/build/bin/llama-cli
export MODEL=/path/to/model.gguf
```

Nothing else is needed. `nlohmann/json.hpp` is vendored, so `g++` is the only
other requirement. Scripts `cd` to their own directory, so you can call them
from anywhere.

```
=== wf_intrusion  (frames=1, seed=42) ===
COMPILE: PASS
--- run ---
frame  2  det= 1  events=1   <-- FIRED
frame  3  det= 2  events=1   <-- FIRED
frame  4  det= 2  events=1   <-- FIRED

total events: 3
expected    : 3

PASS
```

## Run all five

```bash
./run_all.sh 42
```

## Point it at your model

```bash
export LLAMA=$HOME/llama.cpp/build/bin/llama-cli
export MODEL=$HOME/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf
```

Defaults are already those paths.

## The five A->B pairs

| Workflow | A | B | Difficulty it tests |
|---|---|---|---|
| `wf_intrusion` | object_detection | intrusion | 1 frame, no state. Simplest. |
| `wf_queue_length` | object_detection | queue length | 1 frame, counting to a threshold |
| `wf_ppe_compliance` | object_detection | PPE compliance | 1 frame, two box classes, containment |
| `wf_line_crossing` | object_detection | line crossing | **2 frames** - state across frames |
| `wf_wrong_way` | object_detection | wrong way | 2 frames, direction via dot product |

## Adding a new A->B pair

1. copy a file in `workflows/`, edit the `spec` block
2. write `common/templates/<name>.txt` - signature plus numbered TODOs,
   ending mid-function with **no closing brace**
3. add `testdata/frames_<x>.json` and `testdata/cfg_<x>.json`, with
   `expected_events` so a run can pass or fail
4. `./run.sh workflows/wf_<name>.json`

No code changes anywhere.

## Why expected_events matters

Compiling proves the code is valid, never that it is correct. A kernel with
`>` where `>=` belongs compiles perfectly and fires zero times. `expected_events`
turns the harness from a smoke test into a correctness test.

## Notes from building this

Three things cost real time and are worth knowing:

- **`-st` (single turn) is required.** Without it `llama-cli` stays interactive
  and the capture grows without bound. A first attempt produced a 376 MB file.
- **The model echoes the prompt.** Anchor extraction on the ```` ```cpp ````
  fence, not on the prompt text.
- **It sometimes returns the whole function, sometimes just the body.**
  `run.sh` detects which and only prepends the signature when it is missing.
