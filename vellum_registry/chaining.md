# Chaining - generating A -> B, then B -> C

The DAG is built one edge at a time. Each generation is independent, and the
only thing that flows between them is a **type**, never code.

```
A = object_detection        B = line_crossing        C = tailgating
```

## Pass 1 - generate A -> B

```
upstream : object_detection
  emits    region.person
  provides  bbox, class_id, confidence, track_id, label

block    : line_crossing
  requires region.person          SATISFIED
  needs    bbox, track_id         SATISFIED
  emits    event.crossing
  provides  track_id, bbox, direction, timestamp_us, camera_id
```

Legal. Prompt is built, kernel is generated:

```cpp
void stage_line_crossing(const SFrame &prev, const SFrame &curr,
                         const SLineConfig &cfg,
                         std::vector<SStageEvent> &out);
```

## Pass 2 - generate B -> C

**This is the part that matters.** For pass 2, block B is no longer a block -
it is now an *upstream producer*, described by exactly the same fields a task
has.

```
upstream : line_crossing          <- promoted from blocks.json to a producer
  emits    event.crossing
  provides  track_id, bbox, direction, timestamp_us, camera_id

block    : tailgating
  requires region.person, event.crossing     SATISFIED by event.crossing
  needs    track_id, timestamp_us            SATISFIED
  emits    event.usecase
```

Legal. Second kernel generated:

```cpp
void stage_tailgating(const std::vector<SStageEvent> &crossings,
                      const STailgateConfig &cfg,
                      std::vector<SUseCaseEvent> &out);
```

## The rule that makes this work

**A block's declared output IS its interface for the next pass.**

`blocks.json` gives every block an `emits` and a `provides`, in exactly the same
shape as a task's output. So the edge checker does not care whether the upstream
is a model-backed task or a previously generated block - it reads the same two
fields either way.

That is what makes the DAG extend to any depth without new machinery.

## What is NOT passed to pass 2

| Passed | Withheld |
|---|---|
| B's output type | B's generated source code |
| B's semantic tag | B's implementation choices |
| B's carried fields | B's variable names, helper usage |

**Never show the model the previous kernel's code.** If you do, it couples to
that implementation instead of to the type. Regenerate A -> B with a different
seed and C breaks - which defeats the whole point of stage independence.

## Failing early in a chain

The edge check runs per edge, so an impossible chain is rejected at the exact
edge that breaks:

```
object_detection -> crop(head) -> face_recognition -> anpr
                                  ^^^^^^^^^^^^^^^^
                                  REJECTED HERE

face_recognition requires region.face
crop emits region.person.head_candidate
a crop cannot assert a face is present - only face_detection can
```

The first two edges are fine and would have generated correctly. You find out
at edge 3, before spending a token on it.

## Regeneration

Because kernels couple only to types, any single block can be regenerated
without touching its neighbours. Change the tailgating rule, regenerate only
that kernel - line crossing is untouched and still valid.

That property is the reason for the whole design.

## Chains worth supporting

Legal:

```
object_detection -> line_crossing -> tailgating
object_detection -> zone_occupancy
object_detection -> crop(head) -> face_detection -> face_recognition
object_detection -> crop(full) -> license_plate_detection -> anpr
object_detection -> line_crossing -> direction_filter -> correlate
pose_estimation  -> zone_occupancy               (see semantics.md open item)
```

Illegal, and why:

```
crop(head) -> face_recognition        crop cannot assert region.face
face_detection -> anpr                a face is not a number plate
semantic_segmentation -> tailgating   no instances, cannot count people
monocular_depth -> line_crossing      no track_id, no bbox
object_detection -> anpr              needs region.license_plate specifically
```
