# Worked chain: object_detection -> line_crossing -> tailgating

Two generation passes. Each one independent.

## Pass 1 - A -> B

Edge check:

```
object_detection emits region.person, provides [bbox, class_id, confidence, track_id, label]
line_crossing    requires region.person          OK
                 needs    bbox, track_id         OK
LEGAL
```

Section 6 of the prompt, built from the registry:

```
THIS BLOCK
  block          : line_crossing
  input semantic : region.person
  input type     : CObjectDetectionResult
  input provides  : bbox, class_id, confidence, track_id, label
  output semantic: event.crossing
  output type    : SStageEvent
  must fill      : track_id, bbox, direction, timestamp_us, camera_id
  frames         : 2
  libraries      : none

RULE
  A track crossed when the sign of sideOfLine changes between the previous
  frame and the current one, for the same track_id.
```

Generated kernel:

```cpp
void stage_line_crossing(const SFrame &prev, const SFrame &curr,
                         const SLineConfig &cfg,
                         std::vector<SStageEvent> &out);
```

## Pass 2 - B -> C

`line_crossing` is now read as a producer. Same two fields the edge checker
always reads:

```
line_crossing emits event.crossing, provides [track_id, bbox, direction, timestamp_us, camera_id]
tailgating    requires region.person OR event.crossing     OK via event.crossing
              needs    track_id, timestamp_us              OK
LEGAL
```

Section 6:

```
THIS BLOCK
  block          : tailgating
  input semantic : event.crossing
  input type     : std::vector<SStageEvent>
  input provides  : track_id, bbox, direction, timestamp_us, camera_id
  output semantic: event.usecase
  output type    : SUseCaseEvent
  must fill      : track_ids, person_count, timestamp_us, camera_id
  frames         : 1
  libraries      : none

RULE
  Emit when min_persons or more DISTINCT track_ids appear in the incoming
  crossings within window_us of each other.
```

Generated kernel:

```cpp
void stage_tailgating(const std::vector<SStageEvent> &crossings,
                      const STailgateConfig &cfg,
                      std::vector<SUseCaseEvent> &out);
```

## What flowed between the passes

Only this:

```
emits   : event.crossing
provides : track_id, bbox, direction, timestamp_us, camera_id
```

**Not the code.** Pass 2 has no idea how pass 1 was implemented, which is
exactly why pass 1 can be regenerated without breaking pass 2.

## Why tailgating is easier here than from raw detections

From raw detections, tailgating has to work out who is in a zone and count
distinct tracks itself. From crossings, the hard part is already done - it just
groups incoming events by time.

**Decomposing the DAG makes each kernel smaller, and smaller kernels are where
generation is reliable.** If a block does not fit in roughly 50 lines, split the
edge rather than asking for a bigger kernel.
