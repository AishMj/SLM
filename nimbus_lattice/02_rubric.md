# 2 - Scoring

Turns "the code looks fine" into a number that can be compared across models.

| Gate | Check | Points |
|---|---|---|
| G0 | Output is code, not prose or an apology | 10 |
| G1 | Signature matches the skeleton exactly | 15 |
| G2 | Calls nothing outside the allow-list | 15 |
| G3 | Compiles with `-fsyntax-only` | 20 |
| G4 | Passes the positive fixtures | 25 |
| G5 | Passes the negative fixtures | 15 |
| | **Total** | **100** |

## G5 is where models separate

Negative fixtures are the ones that must NOT fire:

- `track_id` is -1 (untracked)
- `class_id` is not a person
- someone approaches the line but never crosses
- a track appears already past the line, with no previous position
- confidence below the configured floor

A model that fires on those has written plausible code that is operationally
useless. Positive fixtures alone will not catch it - the code looks correct
and passes every happy-path test.

## L4 and L5 add two gates

| Gate | Check | Points |
|---|---|---|
| G6 | Fills every `SStageEvent` field the next stage needs | 10 |
| G7 | Actually branches on `hasFace` rather than calling and ignoring it | 10 |

G7 catches a specific and common failure: the model calls the helper because
the prompt mentioned it, then ignores the return value. Stub `hasFace` to
return false for a known track id, and the fixture proves whether the branch
is real.

## Run five seeds

Seeds 42 through 46, `--temp 0`. Report mean AND worst.

A model averaging 85 with a worst of 20 is unusable in an automated pipeline.
Nothing reviews each generation by hand, so the worst case is what ships.
Variance matters more than mean here.

## What the report looks like

```
model                  L1   L2   L3   L4   L5  worst  invented
                                                      helpers
──────────────────────────────────────────────────────────────
model A               100  100   85   70   40    35      0
model B               100   95   75   55   25    20      2
model C               100   90   60   30    0     0      5
```

The useful output is not a winner. It is the column where the numbers fall off
a cliff - that tells you which stages to generate and which to hand-write.
