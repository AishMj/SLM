# ws_reasoning

Generate a custom analytic with an SLM given only the block's **name** and
its input/output field shapes - no algorithm, no skeleton, no fixed
contract.hpp. The counterpart to `ws_cur`, which gives the model a full
English rule plus a numbered-TODO skeleton. Standalone: no dependency on
`ws_cur` or `../common`.

## The question this answers

`ws_cur` tests whether a code-completion model can translate an
already-solved algorithm into C++. `ws_reasoning` tests whether a model can
work the algorithm out itself, from nothing but the block's name and the
shapes of its input and output.

## Layout

```
workflows/           one A->B pair per file - the input. Standalone copy,
                      not a symlink - edits here do not propagate anywhere.
testdata/             frames + config per pair, each config carries
                      expected_events. Standalone copy.
third_party/nlohmann/ vendored JSON library - the only third-party dep.
blocks/               real AI tasks (object_detection, pose_estimation, ...)
                      pulled from AI_HardwareAgnosticLayer/ai_tasks/common -
                      not consumed by the pipeline yet, raw material for
                      building new workflow.json pairs against the real
                      codebase instead of the synthetic one.

gen_types.py          workflow.json -> the minimal C++ this pair needs
                      (InRecord/OutRecord/Config + the function signature).
                      No model involved.
gen_harness.py         workflow.json -> a real, compilable main.cpp that
                      loads testdata/, calls the model's function, checks
                      the event count against expected_events. No model
                      involved.
build_prompt.py        gen_types' output -> what the model actually sees.
                      Handles both chat templates (qwen ChatML, DeepSeek's
                      <|User|>/<|Assistant|><think>).
extract.py             raw model output -> clean C++. Strips DeepSeek's
                      <think> trace, prompt echoes, re-declared types;
                      detects stubs and truncated-mid-think output.
run.sh                 generate -> compile -> run -> PASS/FAIL, with up to
                      3 retries, each with a purpose-built follow-up prompt
                      depending on exactly what went wrong.
run_all.sh              every workflow, one fixed sampling setting, tabulated.
sweep.sh                one workflow through 5 (temp, top_k, seed) combos,
                      each saved to its own out/results/<label>_* folder.
```

## Get it and run it

```bash
# copy just this folder - it is fully standalone
scp -r ws_reasoning newmachine:~/
```

Prerequisites on the target machine:
- g++ with C++14 support (any recent gcc/clang)
- python3, stdlib only - no pip packages needed
- llama.cpp built, with the `llama-cli` binary
- a `.gguf` model - a code model (e.g. qwen2.5-coder) or a reasoning model
  (e.g. DeepSeek-R1-Distill-Qwen-1.5B)

```bash
cd ws_reasoning

export LLAMA=/path/to/llama.cpp/build/bin/llama-cli   # optional - auto-searched
export MODEL=/path/to/your-model.gguf                 # optional - auto-searched
export TEMPLATE=chatml      # for qwen-style code models
# export TEMPLATE=deepseek  # for DeepSeek-R1-Distill

./run.sh workflows/wf_line_crossing.json 42     # one workflow
./run_all.sh 42                                  # every workflow
./sweep.sh workflows/wf_line_crossing.json qwen  # 5 sampling combos, saved
```

`run.sh`/`MODEL`/`LLAMA` auto-search `~/models`, `/opt/models`, `./models`,
`../models` and `~/llama.cpp/build/bin`, `/opt/llama.cpp/build/bin` if the
env vars aren't set.

## Picking a sampling combo

`run.sh` has a combo block near the top (two labelled sections, QWEN and
DEEPSEEK, 5 options each as comments) - exactly one `TEMP`/`TOPK`/`TOPP`
line should be active at a time. Edit the file to switch, or export
`TEMP`/`TOPK`/`TOPP` before calling `run.sh` to override whatever is active
without editing the file (this is what `sweep.sh` does per-combo).

DeepSeek's combo 2 (temp 0.6, top_p 0.95, no top_k restriction) is its own
documented recipe, not a guess - see DeepSeek-R1's usage recommendations.
Greedy decoding (temp=0) is explicitly warned against for that model family:
it causes endless repetition loops.

## What a retry actually means

Each attempt is classified as one of:
- `ok` - compiled, contains real logic. Done, runs against testdata/.
- `stub` - compiled, but the function body is empty/comments only. Retried
  with an explicit "you wrote nothing, try again" prompt.
- `truncated` - a `<think>`-first model ran out of its token budget still
  reasoning, never reached an answer. Not a code bug - retried with a bigger
  budget and a "stop reasoning, commit to an answer" prompt.
- `compile_fail` - real compiler error. Retried with the error fed back.

Every attempt's exact prompt, raw model output, extracted body, compiled
kernel, and build log are saved to `out/attempts/<workflow>_a<N>_*` - nothing
from an earlier attempt is overwritten by a later one.

## Known gap

`gen_types.py` only supports the `ai task -> custom analytic` edge (node A
is a camera event, node B is the block being generated). `custom -> ai task`
and `ai task -> ai task` raise `UnsupportedEdge` - the registry has no
declared input shape for an ai task node to adapt into yet.
