# 5 - Simple evaluation: L3 line crossing

The first level worth measuring. L1 and L2 are sanity checks - every model
passes them.

## What it tests

Can the model hold state between two frames, match a track across them, and
fill a hand-off type completely.

## Run it

```bash
./eval.sh /opt/models/<model>.gguf L3
```

Five seeds, `--temp 0`, scored against `fixtures/L3.json`.

## The fixtures that matter

Positive cases are easy and every model passes them. These are the ones that
separate models:

| Fixture | Must fire? | What it catches |
|---|---|---|
| `crosses_in` | yes | baseline |
| `crosses_out` | yes | direction logic |
| `approaches_but_stops` | no | firing on proximity instead of crossing |
| `untracked` | no | ignoring the `track_id < 0` guard |
| `car_crosses` | no | ignoring `class_id` |
| `new_track_no_history` | no | firing when there is no previous position |
| `low_confidence` | no | ignoring the threshold |
| `sits_exactly_on_line` | no | treating 0.0f as a crossing |

`new_track_no_history` is the one most models fail. A person who appears
already past the line has no previous position - the correct answer is "do not
fire", but the natural code fires.

`sits_exactly_on_line` is second. `sPrev * sCurr < 0` is the correct test.
`sPrev != sCurr` is not, and both look reasonable.

## Scoring

Per `02_rubric.md`. G4 is the positive fixtures, G5 the negative ones.

A model scoring 100 on positives and 0 on negatives has written code that fires
on everything. That is worse than code that never fires, because it looks like
it works.

## What good looks like

```
model            seed  G0  G1  G2  G3  G4  G5  total
────────────────────────────────────────────────────
model-a            42  10  15  15  20  25  15   100
model-a            43  10  15  15  20  25  10    95
model-a            44  10  15  15  20  25  15   100
model-a            45  10  15  15  20  25  15   100
model-a            46  10  15  15  20  25  15   100
                                    mean 99  worst 95
```

Report worst, not just mean. Nothing reviews each generation by hand, so the
worst case is what ships.
