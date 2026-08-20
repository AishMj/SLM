#!/usr/bin/env bash
# run_all.sh [seed] - every reasoning workflow, tabulated: compile attempts +
# final PASS/FAIL against expected_events.
set -u
cd "$(dirname "$0")"
SEED="${1:-42}"

printf "%-18s %-8s %-10s %-6s\n" "workflow" "compile" "attempts" "run"
for wf in workflows/wf_*.json; do
  NAME=$(python3 -c "import json;print(json.load(open('$wf'))['workflow_id'])")
  OUT=$(./run.sh "$wf" "$SEED" 2>&1)
  if echo "$OUT" | grep -q "^COMPILE: PASS"; then
    ATT=$(cat "out/${NAME}_attempts.txt" 2>/dev/null || echo "?")
    if echo "$OUT" | grep -q "^PASS$"; then RUN="PASS"
    elif echo "$OUT" | grep -q "FAIL - compiles but"; then RUN="WRONG"
    else RUN="?"; fi
    printf "%-18s %-8s %-10s %-6s\n" "$NAME" "PASS" "$ATT" "$RUN"
  else
    ATT=$(cat "out/${NAME}_attempts.txt" 2>/dev/null || echo "3")
    printf "%-18s %-8s %-10s %-6s\n" "$NAME" "FAIL" "$ATT" "-"
  fi
done
