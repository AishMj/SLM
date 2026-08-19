#!/usr/bin/env bash
# run.sh <workflow.json> [seed] - generate, compile, RUN, report
set -u
cd "$(dirname "$0")"
# --- locate llama-cli and a model, or explain how to point at them ---
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
  [ -n "${MODEL:-}" ] && { echo "$MODEL"; return; }
  for d in "$HOME/models" /opt/models ./models ../models; do
    m=$(ls "$d"/*.gguf 2>/dev/null | head -1) && [ -n "$m" ] && { echo "$m"; return; }
  done
}

LLAMA=$(find_llama)
MODEL=$(find_model)

if [ -z "$LLAMA" ] || [ ! -x "$LLAMA" ]; then
  echo "ERROR: llama-cli not found."
  echo "  export LLAMA=/path/to/llama.cpp/build/bin/llama-cli"
  exit 1
fi
if [ -z "$MODEL" ] || [ ! -f "$MODEL" ]; then
  echo "ERROR: no .gguf model found."
  echo "  export MODEL=/path/to/model.gguf"
  exit 1
fi
WF="${1:?usage: run.sh workflows/wf_x.json [seed]}"
SEED="${2:-42}"

NAME=$(python3 -c "import json;print(json.load(open('$WF'))['workflow_id'])")
FRAMES=$(python3 -c "import json;d=json.load(open('$WF'));print([n for n in d['nodes'] if n.get('generate_code')][0]['spec']['frames'])")
TD_F=$(python3 -c "import json;print(json.load(open('$WF'))['testdata']['frames'])")
TD_C=$(python3 -c "import json;print(json.load(open('$WF'))['testdata']['config'])")
mkdir -p out

echo "=== $NAME  (frames=$FRAMES, seed=$SEED) ==="

# 1. build the prompt from the workflow
./build_prompt.py "$WF" > out/${NAME}_prompt.txt

# 2. generate
"$LLAMA" -m "$MODEL" -f out/${NAME}_prompt.txt \
    -n 700 -c 8192 -t 4 --temp 0 --top-k 1 --seed $SEED --repeat-penalty 1.0 \
    --no-display-prompt --no-warmup -st -no-cnv 2>/dev/null > out/${NAME}_raw.txt

if [ ! -s out/${NAME}_raw.txt ]; then echo "GEN FAIL: model produced nothing"; exit 1; fi

# 3. rebuild the translation unit: signature from the skeleton + generated body
SKEL=$(python3 -c "import json;print([n for n in json.load(open('$WF'))['nodes'] if n.get('generate_code')][0]['spec']['skeleton'])")
# llama-cli prints a banner, echoes the prompt after '> ', then prints a
# stats line. Keep only what lies between the LAST '> ' and the stats line.
# The model wraps its answer in a ```cpp fence. Take the FIRST fenced block.
# If there is no fence, fall back to everything after the last '> ' echo line.
awk '/^```/{n++; next} n==1{print} n>=2{exit}' out/${NAME}_raw.txt > out/${NAME}_body.txt
if [ ! -s out/${NAME}_body.txt ]; then
  awk '/^> /{buf=""; next} /^\[ Prompt:/{exit} {buf=buf $0 "\n"} END{printf "%s", buf}' \
      out/${NAME}_raw.txt > out/${NAME}_body.txt
fi
sed -i 's/<|im_end|>//' out/${NAME}_body.txt

# The model sometimes returns just the body, sometimes the whole function.
# Only prepend the signature when it did not write one.
if grep -q 'void stage_kernel' out/${NAME}_body.txt; then
  SIG=""            # model wrote the signature itself
else
  SIG=$(grep -v '^\s*//' ../common/templates/$SKEL | sed -n '1,/^{$/p')
fi

{
  echo '#include "contract.hpp"'
  echo '#include <set>'
  echo '#include <algorithm>'
  echo
  [ -n "$SIG" ] && echo "$SIG"
  cat out/${NAME}_body.txt
} > out/${NAME}_kernel.cpp

# 4. COMPILE and LINK against the fixed harness
DEF=""; [ "$FRAMES" = "2" ] && DEF="-DBLOCK_FRAMES_2"
if g++ -std=c++14 -I../common $DEF \
      out/${NAME}_kernel.cpp ../common/helpers.cpp ../common/main.cpp \
      -o out/${NAME}_run 2> out/${NAME}_build.log; then
  echo "COMPILE: PASS"
else
  echo "COMPILE: FAIL"; head -12 out/${NAME}_build.log; exit 1
fi

# 5. RUN it
echo "--- run ---"
./out/${NAME}_run "$TD_F" "$TD_C"
