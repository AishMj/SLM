# 6 - Complex evaluation: L4 and L5

## L4 - consuming a produced type

The stage-2 kernel does NOT start from detections. It starts from the
`SStageEvent` that stage 1 produced. That is the composition rule, and it is
what L4 measures.

```cpp
void stage_face_check(const std::vector<SStageEvent> &in,   // <- stage 1 output
                      const SFrame                   &faceFrame,
                      const SChainConfig             &cfg,
                      std::vector<SUseCaseEvent>     &out);
```

### What it catches

| Failure | How the fixture catches it |
|---|---|
| ignores `in` and re-detects from the frame | fixture passes an empty frame; correct code emits nothing |
| calls `hasFace` but ignores the result | stub returns false for track 8; if it still fires, the branch is fake |
| drops fields from the hand-off | assert `timestamp_us` and both track ids survive to the output |

The middle one is common. Models call a helper because the prompt mentioned it,
then do not branch on the return value. Stub `hasFace` so it returns false for
a known track and the fixture proves whether the branch is real.

### Extra gates

| Gate | Check | Points |
|---|---|---|
| G6 | every `SStageEvent` field the next stage needs is filled | 10 |
| G7 | actually branches on `hasFace` | 10 |

## L5 - cross-camera correlation

A crossing on the source camera, then a face on the target camera, within
`cfg.window_us`.

```cpp
void stage_correlate(const std::vector<SStageEvent> &fromLine,
                     const std::vector<SStageEvent> &fromFace,
                     std::vector<SStageEvent>       &pending,   // MUTABLE, persists
                     const SChainConfig             &cfg,
                     std::vector<SUseCaseEvent>     &out);
```

### The three things it tests

1. **Persistent state.** `pending` is a non-const reference that survives
   between calls. Does the model understand it is not local?
2. **Expiry.** Entries older than `window_us` must be dropped. Forget it and
   `pending` grows without bound - a memory leak in a service that runs for
   months.
3. **Removal on match.** Forget it and one crossing matches every subsequent
   face, forever.

### Fixtures

| Fixture | Expect | Catches |
|---|---|---|
| cross then face inside window | 1 event | baseline |
| cross then face after window | 0 events | missing expiry check |
| face with no preceding cross | 0 events | firing on the second stage alone |
| two crosses, one face | 1 event | matching both to the same face |
| cross, face, then another face | 1 event | not removing on match |
| long idle then a cross | pending stays bounded | leak |

### Expected result

**Most models will fail L5, and that is the finding.** It is the level to
hand-write.

The correlate node is about 40 lines, identical for every workflow, and getting
expiry wrong causes a slow leak that will not show up in testing. Write it once,
test it hard, reuse it everywhere.

Generate L3 and L4. Hand-write L5. This evaluation gives you the evidence for
that split rather than the assertion.
