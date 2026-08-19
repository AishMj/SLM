#!/usr/bin/env bash
# run_all.sh [seed] - every workflow: generate, compile, run, tabulate
cd "$(dirname "$0")"
SEED="${1:-42}"
printf "%-22s %-8s %-8s %-8s %s\n" WORKFLOW GENERATE COMPILE RUN RESULT
printf -- "-%.0s" {1..64}; echo
for wf in workflows/*.json; do
  N=$(python3 -c "import json;print(json.load(open('$wf'))['workflow_id'])")
  OUT=$(timeout 500 ./run.sh "$wf" "$SEED" 2>&1)
  G=$(echo "$OUT" | grep -q "GEN FAIL" && echo FAIL || echo ok)
  C=$(echo "$OUT" | grep -q "COMPILE: PASS" && echo ok || echo FAIL)
  if   echo "$OUT" | grep -q "^PASS"; then R=ok;   V=PASS
  elif echo "$OUT" | grep -q "^FAIL"; then R=ok;   V="WRONG BEHAVIOUR"
  elif [ "$C" = "FAIL" ];              then R="-"; V="COMPILE ERROR"
  else                                      R=ok;  V="ran, no expectation"
  fi
  printf "%-22s %-8s %-8s %-8s %s\n" "$N" "$G" "$C" "$R" "$V"
done
