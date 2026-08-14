#!/usr/bin/env bash
#
# check.sh - ask llama.cpp to write a custom_logic kernel, then see whether it
# compiles. Nothing more. No harness, no test data, no build system.
#
# usage:
#   ./check.sh                 tailgating (default)
#   ./check.sh prompt_x.txt    any other prompt file
#
# needs: g++, llama.cpp built, a GGUF model.
# edit the two paths below to match this machine.

set -u

LLAMA=/opt/llama.cpp/build/bin/llama-cli
MODEL=/opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf

PROMPT="${1:-prompt.txt}"

# ---------------------------------------------------------------------------
# sanity checks first - these are the two things that actually go wrong
# ---------------------------------------------------------------------------

if [ ! -x "$LLAMA" ]; then
    echo "ERROR: llama-cli not found or not executable at:"
    echo "  $LLAMA"
    echo "edit LLAMA at the top of this script"
    exit 1
fi

if [ ! -f "$MODEL" ]; then
    echo "ERROR: model not found at:"
    echo "  $MODEL"
    echo "edit MODEL at the top of this script"
    exit 1
fi

if [ ! -f "$PROMPT" ]; then
    echo "ERROR: prompt file not found: $PROMPT"
    exit 1
fi

if [ ! -f contract.hpp ]; then
    echo "ERROR: contract.hpp not found in the current directory"
    echo "the generated code has nothing to compile against without it"
    exit 1
fi

# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------

echo "=== generating ==="
echo "model  : $(basename "$MODEL")"
echo "prompt : $PROMPT"
echo

# -n 600                max tokens to generate
# -c 8192               context size
# -ngl 99               all layers on GPU. use 0 for CPU only.
# --temp 0.2            low, we want repeatable code not creative code
# -s 42                 fixed seed so two runs are comparable
# --no-display-prompt   do NOT echo the prompt back into stdout.
#                       without this, raw.txt is mostly your own prompt.
# 2>/dev/null           llama.cpp logs progress to stderr - drop it

"$LLAMA" -m "$MODEL" -f "$PROMPT" \
         -n 600 -c 8192 -ngl 99 \
         --temp 0.2 -s 42 \
         --no-display-prompt --no-warmup \
         2>/dev/null > raw.txt

if [ ! -s raw.txt ]; then
    echo "ERROR: model produced no output."
    echo "re-run without 2>/dev/null to see what llama.cpp said."
    exit 1
fi

# ---------------------------------------------------------------------------
# clean
#
# models wrap code in markdown fences even when told not to, and the chat
# template end marker leaks through. strip both.
# ---------------------------------------------------------------------------

sed -e '/^```/d' -e 's/<|im_end|>//' raw.txt > body.cpp

# the model was told not to write #include, so prepend it here
{
    echo '#include "contract.hpp"'
    echo
    cat body.cpp
} > custom_logic.cpp

echo "=== generated ==="
cat custom_logic.cpp

# ---------------------------------------------------------------------------
# compile
#
# -fsyntax-only parses and type-checks without producing a binary. a second or
# two instead of a full build, which is what you want when running this
# repeatedly.
# ---------------------------------------------------------------------------

echo
echo "=== compiling ==="

if g++ -std=c++14 -fsyntax-only custom_logic.cpp 2> err.txt; then
    echo "RESULT: COMPILES"
    rm -f err.txt
    exit 0
fi

echo "RESULT: FAILED"
echo
cat err.txt
echo
echo "common causes:"
echo "  'X was not declared'  -> the model invented a helper that does not"
echo "                           exist. add it to contract.hpp, or name the"
echo "                           real helpers explicitly in the prompt."
echo "  redefinition errors   -> the model redefined the structs. tell it more"
echo "                           firmly that the types already exist."
exit 1
