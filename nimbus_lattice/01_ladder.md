# 1 - The capability ladder

Five levels. Each adds exactly ONE new difficulty, so when a model fails you
know precisely what it failed at. That is the point - a single pass/fail on a
complex task tells you nothing actionable.

| L | Task | New difficulty | Input | Output |
|---|---|---|---|---|
| L1 | Zone occupancy | none - baseline | 1 frame | SUseCaseEvent |
| L2 | Tailgating | distinct counting | 1 frame | SUseCaseEvent |
| L3 | Line crossing | state between frames | 2 frames | SStageEvent |
| L4 | Cross then face | consuming a previous stage | SStageEvent + frame | SUseCaseEvent |
| L5 | Cross-camera correlation | time windows, persistent state | 2 cameras | SUseCaseEvent |

## The composition rule

**Each stage's output type is the next stage's input type.** That is the whole
design, and it is what the SLM has to respect.

```
detections --[L3 kernel]--> SStageEvent --[L4 kernel]--> SUseCaseEvent
   cam 1                    hand-off              cam 2
```

`SStageEvent` carries four things the next stage cannot work without:

| Field | Why the next stage needs it |
|---|---|
| `timestamp_us` | to decide whether the second event is inside the window |
| `camera_id` | to know which stream it came from |
| `track_id` | to identify who, on that camera |
| `bbox` | so stage 2 can crop without re-running detection |

Drop any one of them and the chain breaks. A model that emits a "line crossing
happened" event with no timestamp has written something that cannot be composed
- it compiles, it looks right, and it is useless downstream.

**That is the single most important thing this evaluation measures.**

## L1 - zone occupancy

Emit an event if any tracked person's box centre is inside `cfg.polygon`.
Single frame, single condition. Baseline - every model should pass.

## L2 - tailgating

Count DISTINCT tracked persons inside the zone. Emit if the count reaches
`cfg.min_persons`. Tests whether the model reaches for a set rather than
counting duplicates.

## L3 - line crossing

A person crossed when `sideOfLine` changes sign between the previous frame and
the current one, for the SAME `track_id`. Emit an `SStageEvent` with direction.

First level that needs state. First level that produces a hand-off type.

## L4 - cross then face

Consume the `SStageEvent` from L3. Compute the head region from the carried
`bbox`, call `hasFace`, and emit a `SUseCaseEvent` only if a face is found.

Tests whether the model can consume a produced type rather than starting from
raw detections.

## L5 - cross-camera correlation

A crossing on the source camera, followed by a face on the target camera within
`cfg.window_us`. Emit one event carrying both track ids.

Needs: persistent state across calls, expiry of stale entries, and removal on
match. All three are routinely missed.
