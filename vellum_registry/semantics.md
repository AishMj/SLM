# Semantic tags - how impossible chains get rejected

The core problem this solves:

```
face_detection  -> CObjectDetectionResult
plate_detection -> CObjectDetectionResult      SAME C++ TYPE
```

A type checker sees two identical types and allows `face_crop -> anpr`.
It compiles. It runs. It produces nonsense, because a face is not a number plate.

**The C++ type says how the data is shaped. The semantic tag says what it MEANS.**
Edge legality is decided on the tag, not the type.

---

## The tag taxonomy

```
image.full_frame            an entire camera frame

region.object               a detected object, class unspecified
  region.person             a person
  region.vehicle            a car, truck, bus
  region.bicycle
  region.face               a human face
  region.license_plate      a number plate

mask.instance               per-object pixel mask
mask.semantic               per-pixel class map, no instances

keypoints.pose              COCO 17-point skeleton
depth.map                   per-pixel relative depth

embedding.image             generic image vector
embedding.face              face identity vector

text.generic                text read from an image
text.plate_number           a number plate string

event.crossing              a boundary was crossed
event.usecase               a use case concluded
```

Indentation is subtyping. `region.person` **is a** `region.object`, so anything
accepting `region.object` accepts a person. The reverse is not true.

---

## The legality rule

```
satisfiable(A) = { A.emits } U supertypes(A.emits) U A.subtypes

edge A -> B is LEGAL  iff
    satisfiable(A)  intersects  B.requires
AND B.requires_fields  is a subset of  A.provides
```

Two conditions, both necessary.

### Why `A.subtypes` is in there

A first draft used only `A.emits` and its supertypes. That rejected a legal
edge:

```
object_detection emits region.object
line_crossing    requires region.person

region.object has no supertype that is region.person
-> WRONGLY REJECTED
```

But object_detection genuinely can produce persons - `class_id` selects which.
So a producer must also be able to satisfy any subtype it explicitly declares
it can narrow to. Hence the `subtypes` field in `tasks.json`.

The direction matters and is easy to get backwards:

| | |
|---|---|
| A producer emitting a **parent** | can satisfy a child, IF it declares that child in `subtypes` |
| A producer emitting a **child** | always satisfies the parent |

`semantic_segmentation` declares no subtypes, so it still cannot satisfy
`region.object` - correct, because it cannot separate instances.

### Condition 1 catches the wrong kind of thing

```
face_detection emits region.face
anpr           requires region.license_plate

region.face is not region.license_plate, and not a subtype of it
-> REJECTED
```

### Condition 2 catches the right kind of thing missing a field

```
semantic_segmentation emits mask.semantic, provides [per_pixel_class_id]
line_crossing         requires_fields [bbox, track_id]

no track_id, no bbox
-> REJECTED
```

That second one is subtle and worth stating: semantic segmentation genuinely
sees people. It just cannot tell you *which* person, so crossing is undecidable
from it. The rejection is correct and a type checker would never catch it.

---

## Crop is semantically transparent

The trap in the whole design.

```
crop(region.person, region = head)   ->   emits WHAT?
```

**Not `region.face`.** Cropping the top quarter of a person box gives you a
region that *probably* contains a face. It is a candidate, not an assertion.

Only `face_detection` can assert `region.face`, because only a detector can
confirm a face is actually there.

So `crop` emits a **derived** tag:

```
crop(region.person, head)  ->  region.person.head_candidate
```

which satisfies `face_detection.accepts` (it takes `region.person`), and does
**not** satisfy `face_recognition.requires` (it needs a confirmed `region.face`).

The legal chain is therefore:

```
object_detection -> crop(head) -> face_detection -> face_recognition
   region.person     candidate      region.face      embedding.face
```

and the illegal shortcut is:

```
object_detection -> crop(head) -> face_recognition
                                  REJECTED - needs a confirmed region.face
```

**If a crop could assert what it contains, the whole model collapses.** That is
the rule to defend.

---

## Worked rejections

### face crop -> ANPR

```
producer : face_detection   emits region.face
consumer : anpr             requires region.license_plate

region.face
  parent: region.object
  is region.license_plate in that chain? no.

REJECTED

message: "anpr requires region.license_plate. face_detection emits
          region.face. A face region can never contain a number plate,
          so no code can bridge these. Insert license_plate_detection
          on a region.vehicle instead."
```

### depth -> tailgating

```
producer : monocular_depth  emits depth.map, provides [per_pixel_relative_depth]
consumer : tailgating       requires_fields [track_id, timestamp_us]

tag mismatch AND no track_id
REJECTED for two independent reasons
```

### semantic segmentation -> zone occupancy

```
producer : semantic_segmentation  emits mask.semantic
consumer : zone_occupancy         requires region.object, needs track_id

REJECTED

message: "semantic_segmentation labels pixels but does not separate
          instances, so it cannot count distinct people. Use
          object_detection or instance_segmentation."
```

### pose -> line crossing — LEGAL but worth noting

```
producer : pose_estimation  emits keypoints.pose, provides [bbox, track_id]
consumer : line_crossing    requires region.person, needs [bbox, track_id]

tag: keypoints.pose is not region.person -> would be REJECTED on tag alone
```

**Decision needed.** Pose provides a bbox and a track_id, so it *could* drive
line crossing. Two options:

- declare `keypoints.pose` a subtype of `region.person` — permissive, but then
  anything accepting a person accepts a pose result
- add `region.person` as a second emitted tag on `pose_estimation` — explicit,
  and my recommendation

Recorded as an open decision rather than silently allowed.

---

## Two gates, not one

Validation happens **before** the model is ever called.

| Gate | Where | Behaviour |
|---|---|---|
| Hard | the harness, from this registry | edge rejected, no prompt is built, no tokens spent |
| Soft | the system prompt | the model is told to refuse if asked something impossible |

**The hard gate is what makes it deterministic.** The soft gate is a backstop
for cases the registry has not modelled yet.

Never rely on the model to refuse. A model that refuses correctly 95% of the
time still lets one impossible chain through in twenty, and it will be a
different one each run. The registry refuses the same way every time.
