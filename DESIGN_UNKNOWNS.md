# Unknown areas - SLM-generated custom_logic over CAiTaskResult

Scope: what the SLM consumes is `CAiTaskResult` and its subclasses from
`ai_tasks/common/include`. Nothing else is considered here.

Question from architecture review: **what is not yet defined, and what will bite us.**

---

## 1. What the contract actually gives us today

Six result types, one JSON envelope, discriminated by a `task` field.

| Task type | Payload | Per-object identity |
|---|---|---|
| `object_detection` | `detections[]` - label, class_id, confidence, bbox | `track_id` |
| `instance_segmentation` | `objects[]` - as above + `mask_rle` | `track_id` |
| `pose_estimation` | `poses[]` - bbox + 17 COCO keypoints | `track_id` |
| `monocular_depth` | per-pixel relative depth | none |
| `semantic_segmentation` | per-pixel class map | none |
| `vision_language` | embedding + `top_labels[]` | none |

Geometry is `SBox {x, y, w, h}`, normalised to `[0,1]`, origin top-left.

```
{ "task": "object_detection",
  "detections": [ { "label":"person", "class_id":0,
                    "confidence":0.9, "bbox":[x,y,w,h], "track_id":7 } ] }
```

**That is the entire input surface.** Every gap below follows from what is
absent from it.

---

## 2. The unknowns, ranked by how much they hurt

### 2.1 There is no time. Every target use case is temporal.

`CAiTaskResult` carries no timestamp and no frame index.

Now look at what we are asking the SLM to write:

| Use case | What it actually requires |
|---|---|
| Tailgating | N persons in a zone **within a time window** |
| Line crossing | Position **before and after** a boundary |
| Loitering | **Dwell duration** in a zone |
| Jaywalking | Crossing outside a zone, **sustained over time** |

Not one of these is decidable from a single `CAiTaskResult`. The existing
hand-written apps work around it by counting loop iterations - `window_frames:
75` - which silently assumes a fixed, known, never-dropping frame rate.

**Unknown:** does the result gain `timestamp_us` and `frame_id`, or does
`custom_logic` receive them out-of-band as call arguments?

**Why it matters:** the answer changes every generated rule. "75 frames" and
"3 seconds" are different programs, and only one of them survives a dropped
frame or a variable-rate stream.

**Recommendation:** put monotonic `timestamp_us` in the envelope. Frame counts
are not a time base.

---

### 2.2 There is no camera identity. This blocks the stated goal outright.

Nothing in `CAiTaskResult` or `SDetection` says which stream produced it.

With one camera that is invisible - it is implicit in the process. The moment
there are two, every rule that says "a person" has to say "a person **on which
camera**", and there is no field to carry it.

**Unknown:** does `camera_id` go in the result envelope, or does the runtime
hand `custom_logic` a pre-keyed map of `camera_id -> result`?

**Why it matters:** this is the difference between the current single-camera
apps and the actual product. It cannot be retrofitted into generated code
later - it changes the shape of every function signature the SLM writes.

---

### 2.3 `track_id` semantics are undefined, and the rules are built on it

The header says `-1 = not yet assigned by tracker`. Nothing else is specified.

Open questions, all of which change generated logic:

- Unique **per camera** or globally?
- Stable across an occlusion, or does a re-entry get a new id?
- Reused after a track dies?
- What is the guaranteed lifetime?

**Why it matters:** tailgating is literally `count(distinct track_id in zone)
>= min_persons`. If the tracker splits one person into two ids during an
occlusion, that is a **false tailgate alarm** - and the generated code is
correct C++ that does the wrong thing.

This is the single most likely source of field failures, and the SLM cannot
know about it unless the contract states it.

---

### 2.4 There is no output event type. Half the contract is missing.

`CAiTaskResult` defines what the **AI** produces. There is no counterpart for
what the **use case** concludes.

"Tailgating occurred" currently has no schema anywhere. The existing apps
`printf` and draw on a frame.

**Unknown:** what does `custom_logic` return?

Until that is defined, we cannot specify the function signature the SLM has to
write, which means we cannot write the prompt, which means we cannot evaluate
the output. **This is on the critical path.** A proposal is in section 3.

---

### 2.5 Single-frame result, stateful rules - where does state live?

`CAiTaskResult` is one frame. Dwell counters, alarm latches and crossing
history are not in it.

The existing apps hold state in local containers - `std::map<int,int>
alarmTtl`, `dwellFrames`. If `custom_logic` is a pure function of one result,
it cannot express any of the four target use cases.

**Unknown:** three possible shapes, and they produce completely different
generated code.

| Option | `custom_logic` shape | Consequence |
|---|---|---|
| A - stateless | `f(result) -> events` | Cannot express any temporal rule |
| B - runtime-provided state | `f(result, State&) -> events` | SLM must respect a state API |
| C - windowed input | `f(deque<result>) -> events` | Simplest to generate, highest memory |

**Recommendation:** C for the first iteration. A bounded ring buffer of recent
results makes every listed use case expressible with straight loops, needs no
state API for the SLM to learn, and is by far the easiest thing to verify.

---

### 2.6 `label` is a free-form string with no agreed vocabulary

`SDetection::label` is `std::string`. `class_id` is an int with no stated
mapping.

The SLM will write `d.label == "person"`. If the deployed model emits
`"Person"`, `"pedestrian"` or only `class_id 0`, the rule silently never fires.
**It compiles. It runs. It detects nothing.**

**Unknown:** is there a canonical label set, and is `class_id` or `label` the
authoritative key?

**Recommendation:** make `class_id` authoritative, publish the enum, and have
generated code compare on the id. Strings are for humans.

---

### 2.7 Normalised coordinates are per-image, and do not compose

`SBox` is normalised `[0,1]` against the source frame. That is the right call
for resolution independence within one camera.

But `(0.5, 0.5)` on camera A and `(0.5, 0.5)` on camera B are **unrelated
points in the world**. Any rule of the form "the same person moved from A to B"
needs either a shared ground plane, a homography per camera, or an appearance
embedding to link identities.

**Unknown:** how are two cameras related to each other geometrically, if at all.

**Note:** `vision_language` already returns an L2-normalised embedding. That is
the natural cross-camera identity mechanism and is already in the contract -
but nothing currently says it should be used that way.

---

### 2.8 Cascades have no representation

Two of the target chains are two-stage:

```
obj det -> intrusion -> colour of the person or vehicle
obj det -> line crossing -> compile and check
```

The colour case means: detect, crop, run a second task on the crop, attach the
answer to the original detection.

`CAiTaskResult` has no way to say *"this result is about that detection on that
frame"*. There is no parent reference and no crop provenance.

**Unknown:** how a second-stage result is bound back to the detection that
produced it.

---

### 2.9 Compiling is not the same as being correct

The gate pipeline proves the generated code builds. Nothing proves it is right.

A tailgating rule with the comparison inverted, or with a zone test that never
returns true, **compiles perfectly and reports nothing forever**.

**Unknown:** what the acceptance test is.

**Recommendation:** every use case ships with a small labelled clip set and an
expected event count. Generated code is accepted only if it produces the
expected events on those clips - not merely if it builds. Without this the
whole pipeline validates syntax and nothing else.

---

### 2.10 What exactly is the SLM asked to write?

The existing tailgating app is ~800 lines. The actual decision logic is about
**40 lines** - the rest is config parsing, drawing, video I/O and the main
loop.

**Unknown:** is `custom_logic` the 40-line kernel, or the whole application?

**This determines feasibility more than model choice does.** A 40-line pure
kernel over a typed input is well within a 7B model. An 800-line application
with OpenCV drawing and video I/O is not, and would not be worth generating
even if it were.

**Recommendation:** the kernel only. Everything else is a fixed harness.

---

## 3. Proposed event schema

The missing counterpart to `CAiTaskResult`, in the same style - JSON envelope,
discriminator field, `writeFields`/`readFields`.

```cpp
namespace ai {

/** One use-case conclusion drawn from one or more AI task results. */
struct SUseCaseEvent
{
    std::string  use_case;         // "tailgating", "line_crossing", "intrusion"
    std::string  camera_id;        // which stream concluded it
    int64_t      timestamp_us = 0; // monotonic, when the condition was met
    float        confidence  = 0.0f;

    std::vector<int32_t> track_ids;   // the tracks that caused it
    std::string  zone_id;             // which configured zone, empty if none
    SBox         bbox;                // representative region

    Json         attributes;          // use-case specific: colour, direction, count
};

class CUseCaseEventResult : public CAiTaskResult
{
public:
    AiTaskType type() const noexcept override { return AiTaskType::UseCaseEvent; }
    std::vector<SUseCaseEvent> events;

protected:
    void writeFields(Json &obj) const override;
    bool readFields(const Json &obj) override;
};

} // namespace ai
```

Wire form:

```json
{ "task": "use_case_event",
  "events": [
    { "use_case": "tailgating",
      "camera_id": "cam_01",
      "timestamp_us": 1723377600123456,
      "confidence": 0.87,
      "track_ids": [7, 12],
      "zone_id": "gate_a",
      "bbox": [0.35, 0.40, 0.30, 0.50],
      "attributes": { "persons_in_zone": 2, "window_ms": 2500 } }
  ] }
```

Why this shape:

- **It reuses the existing envelope**, so nothing new is needed to route or
  parse it.
- **`track_ids` gives traceability** - an operator can ask why the event fired.
- **`attributes` is open**, so a new use case does not need a schema change.
  Colour goes in there for the intrusion cascade.
- **`camera_id` and `timestamp_us` are present from day one**, so the
  single-camera case and the multi-camera case have the same shape and the
  generated code does not have to be rewritten later.

---

## 4. Proposed custom_logic contract

What the SLM is asked to produce, given section 2.5 option C:

```cpp
// Generated by the SLM. Everything else is fixed harness code.
//
// history : most recent N results for this camera, newest last.
//           N is configured per use case, guaranteed non-empty.
// cfg     : the use-case JSON block, already parsed.
// out     : events concluded from this frame. Empty is a valid answer.
std::vector<SUseCaseEvent> custom_logic(
        const std::deque<const CAiTaskResult*> &history,
        const Json                             &cfg);
```

Tailgating then becomes roughly this - and this is the whole of what the model
has to write:

```cpp
std::vector<SUseCaseEvent> custom_logic(
        const std::deque<const CAiTaskResult*> &history, const Json &cfg)
{
    std::vector<SUseCaseEvent> out;

    const auto *latest = dynamic_cast<const CObjectDetectionResult*>(history.back());
    if (latest == nullptr) return out;

    const int   minPersons = cfg.value("min_persons", 2);
    const auto  zone       = parseZone(cfg["polygon"]);

    std::set<int32_t> inZone;
    for (const SDetection &d : latest->detections)
    {
        if (d.track_id < 0)          continue;
        if (d.class_id != CLASS_PERSON) continue;

        const float cx = d.bbox.x + d.bbox.w * 0.5f;
        const float cy = d.bbox.y + d.bbox.h * 0.5f;
        if (pointInZone(cx, cy, zone)) inZone.insert(d.track_id);
    }

    if (static_cast<int>(inZone.size()) >= minPersons)
    {
        SUseCaseEvent e;
        e.use_case  = "tailgating";
        e.track_ids.assign(inZone.begin(), inZone.end());
        e.attributes["persons_in_zone"] = inZone.size();
        out.push_back(e);
    }
    return out;
}
```

About 30 lines. Comfortably inside what a 7B code model produces reliably, and
small enough to review by eye.

Note what the harness supplies and the model does **not** have to write:
`pointInZone`, `parseZone`, `CLASS_PERSON`, drawing, video I/O, config loading.
Every helper the generated code may call must be on a published allow-list, or
the model will invent function names that do not exist.

---

## 5. What to settle before writing the prompt

In dependency order. Items 1-4 block prompt design entirely.

| # | Decision | Blocks |
|---|---|---|
| 1 | Is `custom_logic` the kernel or the whole app? | Everything |
| 2 | Function signature - stateless, state object, or history window | Every generated line |
| 3 | Output event schema | Cannot specify the return type |
| 4 | Published helper allow-list | Model invents functions otherwise |
| 5 | `timestamp_us` in the envelope, or passed alongside | All temporal rules |
| 6 | `camera_id` in the envelope | Multi-camera, all of it |
| 7 | `track_id` guarantees - scope, stability, reuse | Correctness of every counting rule |
| 8 | Canonical class vocabulary, id or string | Silent no-fire failures |
| 9 | Acceptance clips per use case | Whether we can tell right from merely-compiling |

---

## 6. The one-line answer for the review

> The model choice is settled. What is not settled is the **contract** -
> `CAiTaskResult` has no time, no camera identity and no output event type, and
> all four target use cases are temporal and eventually multi-camera. Those
> three gaps, plus an undefined `track_id` guarantee, are the real risk. They
> are schema decisions, not model decisions, and they are cheap to fix now and
> expensive to retrofit once generated code exists in the field.
