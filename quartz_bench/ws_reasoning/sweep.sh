#!/usr/bin/env bash
# sweep.sh <workflow.json> <label> - the greedy (temp=0) path is one single
# trajectory; if it stubs out or gets the logic wrong, that alone doesn't
# tell you whether the model CAN do this task. Try 5 (temp, top_k, seed)
# combinations and save every artifact from each into its own directory
# under out/results/<label>_*, so all runs stay inspectable side by side.
set -u
cd "$(dirname "$0")"
WF="${1:?usage: sweep.sh workflows/wf_x.json <label>}"
LABEL="${2:?usage: sweep.sh workflows/wf_x.json <label>}"

NAME=$(python3 -c "import json;print(json.load(open('$WF'))['workflow_id'])")
COMBOS=("0 1 42" "0.7 40 1" "0.7 40 2" "0.7 40 3" "1.0 100 7")
mkdir -p out/results

for combo in "${COMBOS[@]}"; do
  read -r t k s <<< "$combo"
  DEST="out/results/${LABEL}_t${t}_k${k}_s${s}"
  mkdir -p "$DEST"
  echo "############ [$LABEL] temp=$t top_k=$k seed=$s ############"
  # TOPP set explicitly too, so this combo doesn't silently inherit whatever
  # TOPP default happens to be active in run.sh's own combo block.
  TEMP="$t" TOPK="$k" TOPP="1.0" ./run.sh "$WF" "$s" 2>&1 | tee "$DEST/run.log"
  for f in prompt.txt raw.txt body.txt kernel.cpp build.log attempts.txt status.txt; do
    [ -f "out/${NAME}_${f}" ] && cp "out/${NAME}_${f}" "$DEST/${f}"
  done
  echo
done

echo "=== saved to out/results/${LABEL}_* ==="
ls -d out/results/${LABEL}_* 2>/dev/null
