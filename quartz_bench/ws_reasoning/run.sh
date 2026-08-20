#!/usr/bin/env bash
# run.sh <workflow.json> [seed] - generate from a plain-language task (no
# rule, no skeleton, no helper allow-list, no fixed contract.hpp), compile,
# and on failure feed the compiler error back for up to MAX_RETRIES attempts.
# Then RUN against testdata/, and compare. Standalone - no dependency on
# ws_cur or ../common; nlohmann is vendored under third_party/.
set -u
cd "$(dirname "$0")"

find_llama() {
  [ -n "${LLAMA:-}" ] && { echo "$LLAMA"; return; }
  command -v llama-cli 2>/dev/null && return
  for p in "$HOME/llama.cpp/build/bin/llama-cli" \
           /opt/llama.cpp/build/bin/llama-cli \
           ../../llama.cpp/build/bin/llama-cli \
           ../../../llama.cpp/build/bin/llama-cli; do
    [ -x "$p" ] && { echo "$p"; return; }
  done
}
find_model() {
  [ -n "${MODEL_REASON:-}" ] && { echo "$MODEL_REASON"; return; }
  [ -n "${MODEL:-}" ] && { echo "$MODEL"; return; }
  for d in "$HOME/models" /opt/models ./models ../models; do
    m=$(ls "$d"/*.gguf 2>/dev/null | head -1) && [ -n "$m" ] && { echo "$m"; return; }
  done
}

LLAMA=$(find_llama)
MODEL=$(find_model)

if [ -z "$LLAMA" ] || [ ! -x "$LLAMA" ]; then
  echo "ERROR: llama-cli not found. export LLAMA=/path/to/llama-cli"; exit 1
fi
if [ -z "$MODEL" ] || [ ! -f "$MODEL" ]; then
  echo "ERROR: no reasoning .gguf found. export MODEL_REASON=/path/to/model.gguf"; exit 1
fi

WF="${1:?usage: run.sh workflows/wf_x.json [seed]}"
SEED="${2:-42}"
MAX_RETRIES=3

# --- sampling combo - exactly ONE TEMP/TOPK/TOPP line active across BOTH
# blocks below. Pick the block matching TEMPLATE (chatml=qwen, deepseek).
# Uses ${VAR:-default} so an already-exported TEMP/TOPK/TOPP (e.g. from
# sweep.sh, which sets a different one per combo) still wins - this file
# only supplies the default when nothing was already set. ---

# === QWEN (code SLM, TEMPLATE=chatml, no documented sampling recipe - these
#     were our own picks) ===
# 1: greedy baseline. Run with seed 42.
# TEMP="${TEMP:-0}"   TOPK="${TOPK:-1}"   TOPP="${TOPP:-1.0}"
# 2: mild sampling. Run with seed 1.
# TEMP="${TEMP:-0.7}" TOPK="${TOPK:-40}"  TOPP="${TOPP:-1.0}"
# 3: mild sampling, different draw. Run with seed 2.
# TEMP="${TEMP:-0.7}" TOPK="${TOPK:-40}"  TOPP="${TOPP:-1.0}"
# 4: mild sampling, different draw. Run with seed 3.
# TEMP="${TEMP:-0.7}" TOPK="${TOPK:-40}"  TOPP="${TOPP:-1.0}"
# 5: wide/exploratory. Run with seed 7.
# TEMP="${TEMP:-1.0}" TOPK="${TOPK:-100}" TOPP="${TOPP:-1.0}"

# === DEEPSEEK (reasoning SLM, TEMPLATE=deepseek) ===
# 1: greedy baseline (temp=0 disables sampling, top_k/top_p/seed are moot).
#    DeepSeek's own docs warn temp=0 causes endless repetitions - this is a
#    control, not the recommended way to run it. Run with seed 42.
# TEMP="${TEMP:-0}"   TOPK="${TOPK:-1}" TOPP="${TOPP:-1.0}"
# 2: DeepSeek's documented recipe (temp 0.5-0.7, 0.6 recommended, top_p 0.95,
#    no top_k restriction). Run with seed 1. ACTIVE.
TEMP="${TEMP:-0.6}"  TOPK="${TOPK:-0}" TOPP="${TOPP:-0.95}"
# 3: same recipe, different sampling draw. Run with seed 2.
# TEMP="${TEMP:-0.6}"  TOPK="${TOPK:-0}" TOPP="${TOPP:-0.95}"
# 4: same recipe, different sampling draw. Run with seed 3.
# TEMP="${TEMP:-0.6}"  TOPK="${TOPK:-0}" TOPP="${TOPP:-0.95}"
# 5: top of the documented range. Run with seed 1.
# TEMP="${TEMP:-0.7}"  TOPK="${TOPK:-0}" TOPP="${TOPP:-0.95}"

NAME=$(python3 -c "import json;print(json.load(open('$WF'))['workflow_id'])")
FRAMES=$(python3 -c "import gen_types;print(gen_types.build('$WF')['frames'])")
# testdata paths in the workflow file are relative to this folder's own
# testdata/ (a standalone copy, not a symlink), so use the field as-is.
TD_F=$(python3 -c "import json;print(json.load(open('$WF'))['testdata']['frames'])")
TD_C=$(python3 -c "import json;print(json.load(open('$WF'))['testdata']['config'])")
mkdir -p out

echo "=== $NAME  (frames=$FRAMES, seed=$SEED, temp=${TEMP:-0}, top_k=${TOPK:-1}) ==="

# 0. generate the types header and the harness this pair needs. Neither is
#    shown to the model - the header text is embedded in the prompt by
#    build_prompt.py, read from workflow.json the same way.
python3 -c "import gen_types; gen_types.write_header('$WF', 'out/types.hpp')" || exit 1
python3 gen_harness.py "$WF" "out/${NAME}_harness.cpp" || exit 1

# DeepSeek-R1-Distill emits a <think>...</think> trace before its answer -
# needs far more budget than a direct-answer model.
if [ "${TEMPLATE:-chatml}" = "deepseek" ]; then
  NGEN="${NGEN:-1500}"
else
  NGEN="${NGEN:-700}"
fi
# retries carry a longer prompt (previous code + compiler error), and a
# reasoning model needs more room on a retry, not less - scale the budget
# up per attempt rather than using one fixed NGEN for every attempt.
NGEN_GROWTH="${NGEN_GROWTH:-1}"
# n * attempt can exceed context on attempt 3+ for a large NGEN base - if you
# raise NGEN (e.g. for DeepSeek), raise CTX to match (n * MAX_RETRIES + prompt
# headroom). Left at the qwen-safe default here to avoid OOM on this box.
CTX="${CTX:-8192}"
# repeat-penalty 1.0 (off) is fine for a direct-answer model, but a
# <think>-first model that gets stuck can burn its whole budget on a
# repeated line (we saw literal "#include <sstream>" forever). Default it
# higher for the deepseek template specifically.
if [ "${TEMPLATE:-chatml}" = "deepseek" ]; then
  REPEAT="${REPEAT:-1.15}"
else
  REPEAT="${REPEAT:-1.0}"
fi

gen() {  # $1 = prompt file -> writes out/${NAME}_raw.txt. Uses $attempt (global).
  local n="$NGEN"
  [ "$NGEN_GROWTH" = "1" ] && n=$((NGEN * attempt))
  "$LLAMA" -m "$MODEL" -f "$1" \
    -n "$n" -c "$CTX" -t 4 --temp "$TEMP" --top-k "$TOPK" --top-p "$TOPP" --seed $SEED --repeat-penalty "$REPEAT" \
    --no-display-prompt --no-warmup -st -no-cnv 2>/dev/null > out/${NAME}_raw.txt
}

extract_and_build() {
  # strip the model's own echo of the fence/prompt/struct defs - a model
  # returning what it was shown is normal, not an error.
  python3 extract.py < out/${NAME}_raw.txt > out/${NAME}_body.txt

  { echo '#include "types.hpp"'; cat out/${NAME}_body.txt; } > out/${NAME}_kernel.cpp
  EXTRA_LIBS=""
  if grep -q 'opencv2/opencv.hpp' out/${NAME}_kernel.cpp; then
    EXTRA_LIBS=$(pkg-config --cflags --libs opencv4 2>/dev/null)
  fi
  echo "$EXTRA_LIBS" > out/${NAME}_extra_libs.txt
}

compile() {
  EXTRA_LIBS=$(cat out/${NAME}_extra_libs.txt)
  g++ -std=c++14 -Iout -Ithird_party \
      out/${NAME}_kernel.cpp out/${NAME}_harness.cpp \
      $EXTRA_LIBS -o out/${NAME}_run 2> out/${NAME}_build.log
}

# status: "ok" (compiled, real logic) | "stub" (compiled, no logic written -
# never fires) | "truncated" (a <think>-first model ran out of budget still
# reasoning, never reached an answer - not a code bug) | "compile_fail"
status_of() {
  if [ "${TEMPLATE:-chatml}" = "deepseek" ] && python3 -c "
import extract, sys
sys.exit(0 if extract.think_truncated(open('out/${NAME}_raw.txt').read()) else 1)
"; then
    echo "truncated"; return
  fi
  if [ $rc -ne 0 ]; then echo "compile_fail"; return; fi
  if python3 -c "
import extract
import sys
sys.exit(0 if extract.is_stub(open('out/${NAME}_body.txt').read()) else 1)
"; then
    echo "stub"
  else
    echo "ok"
  fi
}

# save every attempt's artifacts under its own name - the plain
# out/${NAME}_* files get overwritten each retry, so without this a failed
# final attempt destroys the evidence of what earlier attempts actually did.
save_attempt() {
  mkdir -p out/attempts
  for f in prompt.txt raw.txt body.txt kernel.cpp build.log; do
    [ -f "out/${NAME}_${f}" ] && cp "out/${NAME}_${f}" "out/attempts/${NAME}_a${1}_${f}"
  done
  echo "$status" > "out/attempts/${NAME}_a${1}_status.txt"
}

attempt=1
./build_prompt.py "$WF" > out/${NAME}_prompt.txt
gen out/${NAME}_prompt.txt
if [ ! -s out/${NAME}_raw.txt ]; then echo "GEN FAIL: model produced nothing"; exit 1; fi
extract_and_build
compile
rc=$?
status=$(status_of)
save_attempt $attempt
while [ "$status" != "ok" ] && [ $attempt -lt $MAX_RETRIES ]; do
  attempt=$((attempt+1))
  if [ "$status" = "truncated" ]; then
    echo "TRUNCATED: ran out of budget mid-think (attempt $((attempt-1))) - retry $attempt/$MAX_RETRIES"
    ./build_prompt.py truncated "$WF" > out/${NAME}_prompt.txt
  elif [ "$status" = "compile_fail" ]; then
    echo "COMPILE: FAIL (attempt $((attempt-1))) - feeding error back, retry $attempt/$MAX_RETRIES"
    ./build_prompt.py fix "$WF" out/${NAME}_kernel.cpp out/${NAME}_build.log > out/${NAME}_prompt.txt
  else
    echo "STUB: no real logic written (attempt $((attempt-1))) - asking again, retry $attempt/$MAX_RETRIES"
    ./build_prompt.py empty "$WF" out/${NAME}_kernel.cpp > out/${NAME}_prompt.txt
  fi
  gen out/${NAME}_prompt.txt
  extract_and_build
  compile
  rc=$?
  status=$(status_of)
  save_attempt $attempt
done

echo "$attempt" > out/${NAME}_attempts.txt
echo "$status" > out/${NAME}_status.txt
if [ "$status" = "ok" ]; then
  echo "COMPILE: PASS  (attempts: $attempt)"
elif [ "$status" = "stub" ]; then
  echo "COMPILE: PASS but STUB after $attempt attempts - no logic written"
  exit 1
elif [ "$status" = "truncated" ]; then
  echo "TRUNCATED after $attempt attempts - never finished reasoning within budget"
  exit 1
else
  echo "COMPILE: FAIL after $attempt attempts"
  head -12 out/${NAME}_build.log
  exit 1
fi

echo "--- run ---"
./out/${NAME}_run "$TD_F" "$TD_C"
