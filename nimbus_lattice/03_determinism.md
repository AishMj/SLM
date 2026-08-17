# 3 - Getting precise, deterministic, reliable output

Three different problems, often confused:

| Want | Means | Lever |
|---|---|---|
| **Deterministic** | same prompt gives byte-identical output every run | sampling settings |
| **Precise** | correct signature, no invented helpers, right shape | prompt structure |
| **Reliable** | works across many use cases, not just the one you tuned | scope + validation |

Fix them in that order. Determinism is free. Precision is prompt engineering.
Reliability is architecture.

---

## A. Determinism - sampling settings

```bash
llama-cli -m model.gguf -f prompt.txt \
    --temp 0            `# greedy - always the highest-probability token` \
    --top-k 1           `# belt and braces, only ever consider one` \
    --seed 42           `# fixed, matters for tie-breaking` \
    --repeat-penalty 1.0 \
    -n 800 -c 8192 -ngl 99 \
    --no-display-prompt --no-warmup
```

### `--repeat-penalty 1.0` is the one people miss

llama.cpp defaults to **1.1**, which penalises tokens that have already
appeared. That is sensible for prose and actively harmful for code, where
repetition is correct and expected:

```cpp
for (const SDetection &d : curr.result.detections)   // "detections" again
    if (d.track_id < 0) continue;                    // "d." again and again
```

With the penalty on, the model drifts to synonyms and invents variable names to
avoid repeating itself. **Set it to 1.0 for code generation.**

### What still breaks determinism

Byte-identical output only holds if all of these are pinned:

- the same GGUF file (hash it - a requantised model is a different model)
- the same llama.cpp build (kernel changes alter floating-point summation order)
- the same `-ngl` value (GPU and CPU paths do not produce identical logits)
- the same batch size

Record all four alongside the generated code. Otherwise "it worked last week"
is unfalsifiable.

---

## B. Precision - prompt structure

This is where the real gains are. Five techniques, strongest first.

### B1. Prefix forcing - end the prompt inside the function

**The single highest-leverage trick.** Do not ask for a function. Write the
opening yourself and let the model continue:

```
Complete this function. Output only the body and the closing brace.

std::vector<SStageEvent> stage_line_cross(
        const SFrame &prev, const SFrame &curr, const SLineConfig &cfg)
{
    std::vector<SStageEvent> out;
```

The signature is now **guaranteed** correct, because the model never wrote it.
G1 in the rubric goes to 100% for free, and there is no markdown fence to strip
because the model is already mid-code.

### B2. Numbered TODO skeleton

A blank page gives you five different structures across five seeds. A numbered
skeleton gives the same structure every time, and any deviation shows up
immediately in a diff.

```cpp
// TODO 1: loop over curr.result.detections
// TODO 2:   skip if track_id < 0
// TODO 3:   skip if class_id != CLASS_PERSON
// TODO 4:   find the same track_id in prev.result.detections
// TODO 5:   if not found, skip
// TODO 6:   compute sPrev and sCurr with sideOfLine
// TODO 7:   crossed when the signs differ; exactly 0.0f is NOT crossed
// TODO 8:   direction "in" when sPrev < 0 and sCurr > 0, else "out"
// TODO 9:   fill EVERY SStageEvent field, then push_back
```

Ordering the TODOs in execution order matters. The model writes top-down.

### B3. Explicit allow-list AND explicit prohibitions

Both halves are needed. Listing what exists is not enough - state what does not.

```
FUNCTIONS YOU MAY CALL - nothing else exists:
  float sideOfLine(const SPt2f &a, const SPt2f &b, float px, float py);

YOU MUST NOT:
  - write #include, main(), printf, cout, or any I/O
  - call any function not listed above
  - redefine any type given above
  - use exceptions, new, delete, malloc
  - use C++17 or later features
```

Invented helpers are the most common compile failure. This is the fix.

### B4. One worked example of a DIFFERENT task

Few-shot teaches shape without giving the answer. Show a completed L1 kernel in
the prompt when asking for L3. The model copies the structure - field order,
guard clauses, naming - and has to work out only the logic.

Do not show the same task. That is not evaluation, it is copying.

### B5. Grammar constraints - `--grammar-file`

llama.cpp can force output to match a GBNF grammar. Useful when you need the
first tokens locked:

```gbnf
root ::= "    " statement+
statement ::= [^\n]+ "\n"
```

Heavier machinery than B1 and B2, and rarely needed once those are in place.
Worth knowing it exists if precision is still short.

---

## C. Reliability - scope and validation

### C1. Keep the kernel small

**Reliability is a function of length.** A 30-line kernel over typed inputs is
comfortably inside a 7B model. A 300-line one is not, and the failure rate
climbs faster than linearly.

The reference application is around 800 lines. The decision logic inside it is
about 40. Generate the 40. Everything else - config parsing, drawing, I/O, the
main loop - is fixed harness written once by a human.

If a use case will not fit in roughly 50 lines, split it into two stages rather
than asking for a bigger kernel.

### C2. Deterministic repair, not free-form retry

When compilation fails, do not re-ask the original question. Send back a
structured repair prompt with exactly three parts:

```
[the original task]

Your previous attempt failed to compile:
[the code]

Compiler error:
[first 1000 chars only]

Return the corrected function only.
```

Truncate the error. C++ errors cascade - one mistake yields twenty messages,
and feeding all of them back buries the real cause. Better still, use
`-fmax-errors=1` so the compiler stops at the first.

### C3. Validate structurally before you validate semantically

Order the gates cheapest-first:

```
1. does it contain the exact signature      grep        instant
2. does it call anything off the allow-list grep -E     instant
3. does it compile                          -fsyntax-only  ~1 s
4. does it pass fixtures                    run         ~1 s
```

No point compiling something that already called an invented function.

### C4. Pin and record

Every generated kernel should be stored with:

- model file name and sha256
- llama.cpp commit
- the exact prompt file
- seed, temperature, `-ngl`
- the compiler command and its exit code

Without this, a regression is unattributable and you cannot tell a model change
from a prompt change.

---

## D. The honest ceiling

None of this makes generation *correct*. It makes it *repeatable* and
*structurally valid*.

A kernel with `>` where `>=` belongs is deterministic, precise, compiles
perfectly, and never fires. That is why G4 and G5 exist in the rubric. Sampling
settings and prompt structure buy you consistency; only fixtures buy you
correctness.

---

## E. Checklist

```
SAMPLING
  [ ] --temp 0
  [ ] --top-k 1
  [ ] --seed fixed
  [ ] --repeat-penalty 1.0        <- the one people miss
  [ ] model sha256 recorded
  [ ] llama.cpp commit recorded

PROMPT
  [ ] ends mid-function so the signature cannot be wrong
  [ ] numbered TODOs in execution order
  [ ] allow-list of callable functions
  [ ] explicit prohibitions
  [ ] one worked example of a different task

SCOPE
  [ ] kernel under ~50 lines
  [ ] anything larger split into stages

VALIDATION
  [ ] signature grep before compiling
  [ ] allow-list grep before compiling
  [ ] -fsyntax-only with -fmax-errors=1
  [ ] positive fixtures
  [ ] negative fixtures            <- where models actually fail
  [ ] 5 seeds, report mean and worst
```
