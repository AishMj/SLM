# vellum_registry

A registry that makes SLM code generation deterministic and refuses impossible
requests before spending a token.

## The problem it solves

```
face_detection          -> CObjectDetectionResult
license_plate_detection -> CObjectDetectionResult     SAME C++ TYPE
```

A type checker allows `face_crop -> anpr`. It compiles, runs, and returns
nonsense forever.

**The C++ type says how data is shaped. The semantic tag says what it means.**
Edges are validated on the tag.

## Files

| File | What |
|---|---|
| `tasks.json` | AI tasks - the six that exist plus face, plate, ANPR, OCR |
| `blocks.json` | business-logic blocks - what the SLM writes |
| `semantics.md` | the tag taxonomy and the legality rule |
| `system_prompt.txt` | invariant system prompt, including how to refuse |
| `prompt_assembly.md` | how a prompt is built from the registry |
| `chaining.md` | generating A->B, then B->C |
| `examples/` | one legal chain, one rejection, both worked through |

## The legality rule

```
edge A -> B is LEGAL iff
    B.requires contains A.emits or one of its supertypes
AND B.needs_fields is a subset of A.carries
```

Both conditions. The first catches the wrong kind of thing; the second catches
the right kind of thing missing a field it needs.

## Two gates

| Gate | Where | Behaviour |
|---|---|---|
| Hard | the harness, from this registry | edge rejected, no prompt built |
| Soft | the system prompt | model told to reply `IMPOSSIBLE: ...` |

**Never rely on the model to refuse.** One that refuses correctly 95% of the
time lets one bad chain through in twenty, differently each run. The registry
refuses identically every time.

## Adding a task

Add an entry to `tasks.json` with its `emits` tag, its `carries` fields, and
what it `accepts`. Nothing else changes - the edge checker and the prompt
builder both read the registry.

## Adding a block for the SLM to write

Add to `blocks.json`: `requires`, `needs_fields`, `frames`, `libraries`,
`emits`, `carries`, `params`, and the rule in one sentence. Add a skeleton
under `templates/`.

## The one trap

**Crop is semantically transparent.** Cropping the head of a person box gives
you a *candidate* head region, not a `region.face`. Only `face_detection` can
assert a face is present.

```
LEGAL    object_detection -> crop(head) -> face_detection -> face_recognition
ILLEGAL  object_detection -> crop(head) -> face_recognition
```

If a crop could assert what it contains, the model collapses. That is the rule
to defend.

## Related

- `../nimbus_lattice/` - how to evaluate whether a model can write these blocks
- `../compile_check/` - the minimal generate-and-compile loop
