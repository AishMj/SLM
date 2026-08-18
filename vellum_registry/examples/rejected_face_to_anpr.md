# Worked rejection: face crop -> ANPR

The case you asked about. Here is exactly what happens.

## The request

> "I have a face crop. Run ANPR on it."

## What the harness does - before any model call

```
producer : face_detection
  emits    region.face
  carries  bbox, confidence, track_id

consumer : anpr
  requires region.license_plate
  needs    bbox

CONDITION 1 - semantic tag
  region.face
    supertypes: region.object
  is region.license_plate among [region.face, region.object] ?
    NO

REJECTED
```

**No prompt is built. No tokens are spent. Same result every time.**

## The message returned

```
ILLEGAL EDGE  face_detection -> anpr

  anpr requires   : region.license_plate
  face_detection  : region.face

  A face region contains no license plate pixels, so no code can bridge
  these two blocks.

  Did you mean:
    object_detection -> crop(full) -> license_plate_detection -> anpr
```

Suggesting the legal alternative matters. A bare rejection tells the user they
are wrong; a rejection with a route tells them what to draw instead.

## If it somehow reaches the model

The registry should catch this. The system prompt is the backstop:

```
IMPOSSIBLE: a face region cannot produce a number plate reading because a
face crop contains no license plate pixels
```

## Why not just let the model try

It would succeed. That is the problem.

Given a face crop and asked for ANPR, a code model will happily write something
that calls an OCR helper on the crop and returns whatever comes back. It
compiles. It runs. It returns garbage strings forever, and nothing in the
pipeline flags it.

**The registry refuses identically every time. A model refuses most of the
time.** For a deterministic system, most of the time is not a property.
