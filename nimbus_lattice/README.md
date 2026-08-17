# nimbus_lattice

Evaluation instrument for code-generating small models.

Measures where a model's capability runs out across a graded ladder of tasks,
rather than producing a single pass/fail that tells you nothing actionable.

## Read in this order

| File | What |
|---|---|
| `01_ladder.md` | five levels, each adding exactly one difficulty |
| `02_rubric.md` | scoring gates, 100 points |
| `03_determinism.md` | how to get repeatable, precise output |
| `04_inputs.md` | what to feed the model, and what to withhold |
| `05_eval_simple.md` | running level 3 |
| `06_eval_complex.md` | levels 4 and 5 |

## Files

```
contract.hpp        types the generated kernels compile against
prompts/            one prompt per level
fixtures/           positive and negative cases per level
eval.sh             generate 5 seeds, score, print a row each
```

## Run

```bash
chmod +x eval.sh
./eval.sh /path/to/model.gguf L3
```

Edit `LLAMA` at the top of `eval.sh` first.

## The two ideas worth knowing

**Each stage's output type is the next stage's input type.** That is the whole
composition contract. A stage that emits a conclusion without a timestamp,
camera id, track id and bbox has produced something that cannot be composed -
it compiles, it looks right, and the next stage cannot use it.

**Negative fixtures are where models separate.** Positive cases are easy and
everything passes them. The cases that must NOT fire - untracked detections,
wrong class, someone who approaches but never crosses, a track with no history -
are what distinguish a working kernel from plausible code.

## Expected shape of the result

```
model      L1    L2    L3    L4    L5   worst
──────────────────────────────────────────────
A         100   100    85    70    40     35
B         100    95    75    55    25     20
C         100    90    60    30     0      0
```

The useful output is not a winner. It is the column where the numbers fall off
a cliff, because that tells you which stages to generate and which to
hand-write.
