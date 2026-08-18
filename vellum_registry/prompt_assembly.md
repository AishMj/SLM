# How a prompt is assembled

The prompt is never written by hand. It is built from the registry, so the
contract and the prompt cannot drift apart.

## The seven sections, in this order

Order matters. The model reads top-down and continues from the last thing it
sees.

| # | Section | Source |
|---|---|---|
| 1 | System prompt | `system_prompt.txt` - invariant |
| 2 | Types | `contract.hpp`, verbatim |
| 3 | Allow-list | fixed, plus `blocks.json:libraries` |
| 4 | Prohibitions | invariant |
| 5 | Worked example | a completed kernel for a DIFFERENT block |
| 6 | This block | derived from the registry, see below |
| 7 | Skeleton | `templates/`, ends mid-function |

## Section 6 is the only part that varies

Everything in it comes from the registry - nothing is typed by a human.

```
THIS BLOCK

  block          : line_crossing                 blocks.json key
  input semantic : region.person                 upstream task's emits
  input type     : CObjectDetectionResult        upstream task's cpp_result
  input provides  : bbox, class_id, confidence,   upstream task's provides
                   track_id, label
  output semantic: event.crossing                blocks.json emits
  output type    : SStageEvent                   contract.hpp
  must fill      : track_id, bbox, direction,    blocks.json provides
                   timestamp_us, camera_id
  frames         : 2                             blocks.json frames
  libraries      : none                          blocks.json libraries
  params         : line_a, line_b,               blocks.json params
                   min_confidence_x100

RULE
  A track crossed when the sign of sideOfLine changes between the previous
  frame and the current one, for the same track_id.
```

## Assembly, in outline

```python
def build_prompt(tasks, blocks, upstream_task, block_name):
    up  = tasks["tasks"][upstream_task]
    blk = blocks["blocks"][block_name]

    # HARD GATE - runs before anything is built
    ok, reason = check_edge(up, blk)
    if not ok:
        raise IllegalEdge(reason)      # no prompt, no tokens spent

    return "\n\n".join([
        SYSTEM_PROMPT,
        CONTRACT_HPP,
        allow_list(blk["libraries"]),
        PROHIBITIONS,
        worked_example(exclude=block_name),
        this_block(up, blk),
        skeleton(block_name),
    ])


def check_edge(producer, consumer):
    emitted = producer["outputs"][0]["emits"]
    lineage = supertypes(emitted)              # region.person -> region.object

    if not any(t in consumer["requires"] for t in lineage):
        return False, (f"{consumer_name} requires {consumer['requires']}, "
                       f"{producer_name} emits {emitted}")

    missing = set(consumer["requires_fields"]) - set(producer["outputs"][0]["provides"])
    if missing:
        return False, f"{producer_name} does not carry {sorted(missing)}"

    return True, ""
```

## Libraries

`blocks.json` provides a `libraries` list per block. Only `crop` currently
declares `opencv`; everything else is empty and gets standard library only.

The allow-list section is generated from that field, so a block cannot use a
library it did not declare - the model is never told the library exists.

```
LIBRARIES YOU MAY USE
  none - C++14 standard library only
```

or, for `crop`:

```
LIBRARIES YOU MAY USE
  OpenCV - only these calls:
    cv::Rect, cv::Mat::operator()(cv::Rect)
  Nothing else from OpenCV. No imread, no imwrite, no imshow, no VideoCapture.
```

Naming the permitted **calls**, not just the library, matters. "You may use
OpenCV" invites `cv::imshow`. A list of four symbols does not.

## Why not hand the model the whole workflow

It would implement the wrong node. Each prompt describes exactly one block, its
immediate upstream, and its immediate downstream. Nothing else.

The model also never sees the previous block's **implementation** - only its
type and semantic tag. That is what keeps blocks independent, and it is what
makes chaining work.
