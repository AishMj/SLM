#!/usr/bin/env bash
#
# eval.sh MODEL LEVEL - generate 5 times, score each, print a row per seed.
#
#   ./eval.sh /opt/models/some-model.gguf L3
#
# Scores G0 to G3 here. G4 and G5 need the fixture runner, which links the
# generated kernel against a main that replays fixtures/L3.json.

set -u

LLAMA=/opt/llama.cpp/build/bin/llama-cli
MODEL="${1:?usage: eval.sh MODEL LEVEL}"
LEVEL="${2:-L3}"

case "$LEVEL" in
  L1) PROMPT=prompts/L1_zone.txt      ; SIG="stage_zone_occupancy" ;;
  L3) PROMPT=prompts/L3_linecross.txt ; SIG="stage_line_crossing"  ;;
  L4) PROMPT=prompts/L4_cascade.txt   ; SIG="stage_face_check"     ;;
  *)  echo "unknown level $LEVEL"; exit 1 ;;
esac

[ -x "$LLAMA" ]   || { echo "llama-cli not at $LLAMA"; exit 1; }
[ -f "$MODEL" ]   || { echo "model not at $MODEL";     exit 1; }
[ -f "$PROMPT" ]  || { echo "prompt not at $PROMPT";   exit 1; }

mkdir -p out
NAME=$(basename "$MODEL" .gguf)

printf "%-34s %-4s %5s %4s %4s %4s %4s %6s\n" MODEL LVL SEED G0 G1 G2 G3 TOTAL

for SEED in 42 43 44 45 46; do
    GEN="out/${NAME}_${LEVEL}_${SEED}.cpp"

    # --temp 0        greedy, no sampling randomness
    # --top-k 1       belt and braces
    # --repeat-penalty 1.0   THE ONE PEOPLE MISS. default 1.1 harms code,
    #                        because code legitimately repeats tokens.
    "$LLAMA" -m "$MODEL" -f "$PROMPT" \
             -n 800 -c 8192 -ngl 99 \
             --temp 0 --top-k 1 --seed $SEED --repeat-penalty 1.0 \
             --no-display-prompt --no-warmup \
             2>/dev/null > out/raw_$SEED.txt

    # the prompt ended mid-function, so the model continues the body.
    # rebuild the whole translation unit around it.
    {
        echo '#include "contract.hpp"'
        echo '#include <set>'
        echo '#include <algorithm>'
        echo
        sed -n "/^void ${SIG}/,\$p" "$PROMPT" | sed '$d'   # signature + TODOs
        sed -e '/^```/d' -e 's/<|im_end|>//' out/raw_$SEED.txt
    } > "$GEN"

    S=0
    grep -q "$SIG"        "$GEN" && S=$((S+10))    # G0 produced code
    grep -q "void $SIG("  "$GEN" && S=$((S+15))    # G1 signature intact
    ! grep -qE '\b(computeIoU|isInside|getCrop|detectFace|cv::|std::cout|printf)\b' \
        "$GEN"                    && S=$((S+15))    # G2 nothing off the allow-list
    g++ -std=c++14 -fsyntax-only -I. "$GEN" 2>/dev/null && S=$((S+20))  # G3 compiles

    printf "%-34s %-4s %5s %4s %4s %4s %4s %6s\n" \
        "$NAME" "$LEVEL" "$SEED" \
        "$(grep -q "$SIG" "$GEN" && echo 10 || echo 0)" \
        "$(grep -q "void $SIG(" "$GEN" && echo 15 || echo 0)" \
        "$(! grep -qE '\b(computeIoU|isInside|getCrop|detectFace|cv::)\b' "$GEN" && echo 15 || echo 0)" \
        "$(g++ -std=c++14 -fsyntax-only -I. "$GEN" 2>/dev/null && echo 20 || echo 0)" \
        "$S"
done

echo
echo "generated kernels are in out/ - diff them across seeds to see variance"
