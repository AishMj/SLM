# samples

The data at every hop of the chain, as real files rather than prose.

Read them in order - each file is the input to the step that produced the next.

| File | Hop | Type | Produced by |
|---|---|---|---|
| `workflow.json` | - | the drawn flow | the UI |
| `cam01_frames.json` | 1 | `CObjectDetectionResult` | node n1, person detection |
| `stage_events.json` | 2 | **`SStageEvent`** | node n2, the SLM-written kernel |
| `cam02_frames.json` | 3 | `CObjectDetectionResult` | node n3, face detection |
| `expected_output.json` | 4 | `SUseCaseEvent` | node n4, correlate |

## The chain

```
cam01_frames.json ──[ n2  SLM-written ]──> stage_events.json ──┐
                                                                ├──[ n4 ]──> expected_output.json
cam02_frames.json ─────────────────────────────────────────────┘
```

## What the sample proves

**Hop 2 is the one that matters.** `stage_events.json` contains exactly one
event - track 7 crossing at 1723377600400000. Look at what it carries:

```json
{ "stage": "line_crossing", "camera_id": "cam_01",
  "timestamp_us": 1723377600400000, "track_id": 7,
  "bbox": [0.45, 0.62, 0.06, 0.12], "direction": "in" }
```

Every one of those fields is consumed downstream. Drop `timestamp_us` and the
correlate node cannot test the window. Drop `bbox` and stage 2 has to re-run
detection. Drop `camera_id` and you cannot tell which stream it came from.

**A kernel that emits `{"use_case":"line_crossing"}` and nothing else compiles
perfectly and breaks the chain.** That is what gate G6 in the rubric checks.

## The negative case is in here too

`cam02_frames.json` has a second face at `1723377608000000` - **7.6 seconds**
after the crossing, against a 5000 ms window. It must NOT match.

`expected_output.json` has one event, not two. If a correlate implementation
produces two, it skipped the window check.

## Using them

The frames files feed the harness directly. The workflow file is what the
prompt builder decomposes - see `04_inputs.md`.
