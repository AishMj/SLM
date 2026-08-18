# Can a small reasoning model author blocks/*.json?

Your question: the user draws a flow and types "line crossing detection using
object detection". Can DeepSeek-R1-Distill-1.5B produce the block spec, which
the code model then implements?

**Yes, but not by free generation.** Constrain it three ways.

## The two-model split

```
user text  --->  REASONING MODEL  --->  blocks/<name>.json  --->  CODE MODEL  --->  kernel.cpp
                 "what block is this"    validated              "write it"
```

Different jobs, different difficulty. Authoring a spec is a *classification and
filling* task, not open composition - which is why a small model can do it.

## Why free generation fails at 1.5B

Asked to invent a whole JSON, a 1.5B model will:

- invent semantic tags that are not in the taxonomy
- get `requires` and `emits` backwards
- put `track_id` in `requires_fields` for an upstream that has no tracker
- emit valid JSON with semantically wrong content, which is the worst outcome
  because it looks correct

## Constraint 1 - closed vocabularies

Never ask for free text where a menu exists. Every field except `rule` and
`description` has a fixed set of legal values, listed in
`block_schema.json:_allowed_values`.

Put the menu in the prompt:

```
requires: choose one or more from this list ONLY
  region.person  region.vehicle  region.object  region.face
  region.license_plate  keypoints.pose  mask.semantic  depth.map
  event.crossing  event.usecase
```

Anything outside the list is rejected by the validator, not argued with.

## Constraint 2 - grammar-constrained decoding

llama.cpp can force output to match a GBNF grammar. For a fixed-shape JSON this
removes malformed output entirely:

```gbnf
root       ::= "{" ws name ws "," ws requires ws "," ws frames ws "," ws rule ws "}"
name       ::= "\"name\":" ws "\"" [a-z_]+ "\""
frames     ::= "\"frames\":" ws "\"" ("1" | "2" | "n") "\""
requires   ::= "\"requires\": [" ws tag (ws "," ws tag)* ws "]"
tag        ::= "\"" ("region.person" | "region.vehicle" | "region.object" |
                     "region.face" | "keypoints.pose" | "event.crossing") "\""
```

Used with `--grammar-file`. The model cannot emit `"frames": "7"` because the
grammar has no path to it.

## Constraint 3 - validate before accepting

Three checks, all mechanical:

```
1. schema     every required field present, every value in its allowed set
2. edge       does the proposed upstream actually satisfy requires + requires_fields
3. duplicate  does a block with this name already exist
```

Check 2 is the important one. If the model writes:

```json
{ "name": "line_crossing", "requires": ["keypoints.pose"],
  "requires_fields": ["bbox", "track_id"] }
```

the edge checker rejects it immediately - pose provides no `track_id`. The
model's mistake never reaches the code generator.

## What the reasoning model is actually asked

Not "write a block". Rather:

```
The user drew:  object_detection -> [custom analytic]
The user typed: "line crossing detection"

object_detection emits region.person and provides
  bbox, class_id, confidence, label, track_id

Answer these six questions. Choose only from the lists given.

1. requires        which tags does this analytic consume?
2. requires_fields which of the provided fields does it need?
3. frames          1, 2, or n - does it need history?
4. state           none, per_track, or global
5. emits           what tag does it produce?
6. rule            one sentence describing the condition
```

Six constrained answers. That is well within a 1.5B model, and every one is
checkable.

## Honest limits

| | 1.5B reasoning | 7B+ |
|---|---|---|
| Known pattern, named analytic | usually right | reliable |
| Novel analytic, vague description | often wrong `frames` or `state` | usually right |
| The `rule` sentence | vague, needs editing | usable |

**`frames` is the field it gets wrong most.** Anything involving movement,
direction, dwell or "before and after" needs 2 or n, and a small model
frequently answers 1 because the description does not say the word "previous".

Mitigation: derive `frames` from keywords in the user text rather than asking
the model at all.

```
crossing, direction, wrong way, entering, exiting, moving  -> 2
dwell, loitering, abandoned, queue over time               -> n
otherwise                                                   -> 1
```

Deterministic, and it removes the field a small model is worst at.

## Recommended flow

```
user text
   |
   v
keyword pass          -> frames, state           deterministic, no model
   |
   v
reasoning model       -> requires, emits, rule   constrained by grammar
   |
   v
validator             -> schema + edge check     reject or accept
   |
   v
human approval        -> first time only
   |
   v
blocks/<name>.json    -> now permanent, deterministic forever
```

**First occurrence is reviewed. Every occurrence after is automatic.** Same
growing-whitelist idea as the registry itself.
