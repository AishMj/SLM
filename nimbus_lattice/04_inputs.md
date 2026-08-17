# 4 - What to feed the SLM

`workflow.json` describes what the USER wants. It says nothing about how to
express it in code. The model needs both, plus the shape of its neighbours in
the chain.

**Do not hand the whole workflow to the model.** The harness decomposes it into
one prompt per stage. Each kernel sees only its own node and the types on
either side of it.

---

## The six inputs

| # | Input | Comes from | Why the model needs it |
|---|---|---|---|
| 1 | Node spec | `workflow.json`, one node | the rule to implement, and its parameters |
| 2 | Input type | the upstream node's output | what the function receives |
| 3 | Output type | the downstream node's input | what it must produce, and every field to fill |
| 4 | Type definitions | `contract.hpp` | so it does not invent or redefine them |
| 5 | Allow-list | fixed | what it may call - nothing else exists |
| 6 | Skeleton | generated per stage | signature plus numbered TODOs |

Inputs 4, 5 and 6 are boilerplate the harness assembles. Only 1, 2 and 3 change
per node - and 2 and 3 are derived from the edges, not written by hand.

---

## workflow.json

What the UI produces when the user draws the flow.

```json
{
  "workflow_id": "wf_0001",
  "name": "gate entry with face check",

  "nodes": [
    { "id": "n1",
      "type": "person_detection",
      "camera": "cam_01",
      "params": { "min_confidence": 0.5, "classes": ["person"] } },

    { "id": "n2",
      "type": "line_crossing",
      "camera": "cam_01",
      "params": {
        "line": { "a": [0.20, 0.50], "b": [0.80, 0.50] },
        "direction_filter": "in",
        "min_confidence": 0.5 } },

    { "id": "n3",
      "type": "face_detection",
      "camera": "cam_02",
      "params": { "min_confidence": 0.6 } },

    { "id": "n4",
      "type": "correlate",
      "params": { "window_ms": 5000 } }
  ],

  "edges": [
    { "from": "n1", "to": "n2" },
    { "from": "n2", "to": "n4" },
    { "from": "n3", "to": "n4" }
  ]
}
```

---

## How the harness decomposes it

For each node that needs generated code, walk the edges to find the types on
either side:

```
node n2 - line_crossing
  upstream   n1 person_detection  -> input  type CObjectDetectionResult
  downstream n4 correlate         -> output type SStageEvent
```

That is the whole derivation. The edges give you the types; you never state
them by hand, which is what stops the chain drifting out of sync.

```python
TYPE_OF_NODE = {
    "person_detection": "CObjectDetectionResult",
    "line_crossing":    "SStageEvent",
    "face_detection":   "SStageEvent",
    "correlate":        "SUseCaseEvent",
}

def build_prompt(wf, node_id):
    node = find_node(wf, node_id)

    upstream   = [e["from"] for e in wf["edges"] if e["to"]   == node_id]
    downstream = [e["to"]   for e in wf["edges"] if e["from"] == node_id]

    in_type  = TYPE_OF_NODE[find_node(wf, upstream[0])["type"]]
    out_type = TYPE_OF_NODE[find_node(wf, downstream[0])["type"]]

    return TEMPLATE.format(
        contract   = CONTRACT_HPP_TEXT,
        allow_list = ALLOW_LIST_TEXT,
        in_type    = in_type,
        out_type   = out_type,
        params     = json.dumps(node["params"], indent=2),
        skeleton   = SKELETONS[node["type"]],
    )
```

**A node with two upstreams is a correlate node.** Those need persistent state
and a time window - hand-write them. See section 6.

---

## What the model must NOT be given

| Withheld | Why |
|---|---|
| the whole workflow.json | irrelevant nodes invite the model to implement the wrong one |
| other cameras' node specs | it will try to reach across cameras inside one kernel |
| video paths, model paths, output paths | not its concern, and it will emit I/O code |
| the previous stage's implementation | it should code against the type, not the code |

The last one matters most. If the model sees how stage 1 was implemented, it
couples to that implementation. Give it the type and nothing else - that is what
keeps the stages independent.

---

## Params: from JSON to a struct

Do not hand raw JSON to the kernel. The harness parses `params` into a typed
config struct and passes that. Two reasons:

- the model cannot mistype a key - `cfg.min_persons` fails at compile time,
  `cfg["min_persons"]` fails silently at runtime
- no JSON library is needed inside the kernel

```json
"params": { "line": { "a": [0.20, 0.50], "b": [0.80, 0.50] },
            "min_confidence": 0.5 }
```

becomes

```cpp
struct SLineConfig {
    SPt2f a;
    SPt2f b;
    int   min_confidence_x100;   // integer - avoids float comparison in the kernel
};
```

Note `min_confidence_x100`. Confidence arrives as a float; comparing floats in
generated code is a source of subtle bugs. An integer threshold removes the
question entirely.

---

## The assembled prompt

Everything above, in this order. Order matters - the model reads top-down and
the last thing it sees is what it continues from.

```
1. ROLE          one line
2. TYPES         from contract.hpp, verbatim
3. ALLOW-LIST    functions and constants that exist
4. PROHIBITIONS  what it must not do
5. WORKED EXAMPLE  a completed kernel for a DIFFERENT stage
6. THIS STAGE    input type, output type, params, the rule in plain English
7. SKELETON      signature plus numbered TODOs, ending mid-function
```

Section 7 ends inside the function body so the model continues rather than
starts. The signature is then guaranteed correct because the model never
wrote it. See `03_determinism.md` section B1.

---

## Worked: what node n2 actually receives

```
THIS STAGE

  node id     : n2
  type        : line_crossing
  camera      : cam_01
  input type  : CObjectDetectionResult   (from node n1, person_detection)
  output type : SStageEvent              (to node n4, correlate)

  params:
    line.a              = (0.20, 0.50)
    line.b              = (0.80, 0.50)
    direction_filter    = "in"
    min_confidence_x100 = 50

RULE
  A person crossed when the sign of sideOfLine changes between the previous
  frame and the current one, for the SAME track_id. Emit one SStageEvent per
  crossing. Fill every field: stage, camera_id, timestamp_us, track_id, bbox,
  direction, confidence. The next stage cannot work without them.

COMPLETE THIS FUNCTION. Output only the body and the closing brace.

void stage_line_crossing(const SFrame &prev, const SFrame &curr,
                         const SLineConfig &cfg,
                         std::vector<SStageEvent> &out)
{
    // TODO 1: loop over curr.result.detections
    // TODO 2:   skip if track_id < 0
    // TODO 3:   skip if class_id != CLASS_PERSON
    // TODO 4:   skip if confidence * 100 < cfg.min_confidence_x100
    // TODO 5:   find the same track_id in prev.result.detections; skip if absent
    // TODO 6:   sPrev = sideOfLine(cfg.a, cfg.b, prevBox.cx(), prevBox.cy())
    //           sCurr = sideOfLine(cfg.a, cfg.b, currBox.cx(), currBox.cy())
    // TODO 7:   crossed when signs differ; exactly 0.0f counts as NOT crossed
    // TODO 8:   direction "in" when sPrev < 0 and sCurr > 0, otherwise "out"
    // TODO 9:   fill EVERY SStageEvent field and push_back onto out
```

That is the complete input for one node. Roughly 2,000 tokens with the contract
included - comfortable inside a 16K window with room for the answer.

---

## Which nodes to generate, and which to hand-write

| Node kind | Generate? | Why |
|---|---|---|
| single-camera rule, one input edge | yes | 30-50 lines, well inside model capability |
| two input edges (correlate) | **no** | persistent state, expiry, time windows - see 06 |
| detection nodes | no | these run a model, no logic to write |

The correlate node is the one to hand-write. It is roughly 40 lines, it is the
same 40 lines for every workflow, and getting expiry wrong leaks memory in a
service that runs for months. Write it once, test it properly, reuse it.
