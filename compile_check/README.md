# compile_check

Smallest possible loop: ask an SLM for a `custom_logic` kernel, see if it compiles.
No harness, no test data, no build system.

## Files

| File | What it is |
|---|---|
| `check.sh` | generate with llama.cpp, strip fences, compile |
| `contract.hpp` | the types the generated code compiles against |
| `prompt.txt` | the prompt, ChatML-wrapped for Qwen |

## Use

```bash
chmod +x check.sh
./check.sh
```

Edit `LLAMA` and `MODEL` at the top of `check.sh` first.

## Pasting code from a GUI tool instead

If the code came from GPT4All, LM Studio or a browser, skip `check.sh`:

```bash
nano custom_logic.cpp          # paste, then Ctrl+O Enter Ctrl+X
g++ -std=c++14 -fsyntax-only custom_logic.cpp
```

Add `#include "contract.hpp"` at the top if the code is only a function.
If it is a complete program with its own `main()`, compile it standalone:

```bash
g++ -std=c++14 -o prog custom_logic.cpp && ./prog
```

## Why -fsyntax-only

Parses and type-checks without producing a binary. A second or two instead of a
full build, which is what you want when running this repeatedly.

## Changing the use case

Edit only the `TASK` paragraph in `prompt.txt`. The contract stays fixed - that
is the whole workflow-builder idea in miniature.
