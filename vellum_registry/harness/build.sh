#!/usr/bin/env bash
# build.sh <block_name> - compile the generated kernel against the fixed harness
#
# reads blocks/<block_name>.json to decide which signature the harness expects.

set -u
BLOCK="${1:?usage: build.sh <block_name>}"
SPEC="blocks/${BLOCK}.json"

[ -f "$SPEC" ] || { echo "no such block: $SPEC"; exit 1; }

# frames = 2 selects the two-frame signature in main.cpp
FRAMES=$(python3 -c "import json;print(json.load(open('$SPEC'))['frames'])")
DEF=""
[ "$FRAMES" = "2" ] && DEF="-DBLOCK_FRAMES_2"

# libraries come from the same json, so a block cannot link something it did
# not declare
LIBS=$(python3 -c "
import json
l=json.load(open('$SPEC'))['libraries']
print('\$(pkg-config --cflags --libs opencv4)' if 'opencv' in l else '')
")

echo "block   : $BLOCK"
echo "frames  : $FRAMES"
echo "defines : ${DEF:-none}"
echo

set -x
g++ -std=c++14 -Wall -Iinclude $DEF \
    generated/kernel.cpp \
    harness/helpers.cpp \
    harness/main.cpp \
    $LIBS \
    -o run_block
