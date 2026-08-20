# blocks/

One JSON file per real AI task, sourced directly from
`/home/h412581/July2026/AI_HardwareAgnosticLayer/ai_tasks/common/include/*.hpp` -
not the synthetic contract used in `quartz_bench/common/`. These are the
actual camera events (`kind: "camera_event"`) available as node A in a
workflow.

| File | Real C++ result type | Cardinality |
|---|---|---|
| `object_detection.json` | `CObjectDetectionResult` | per_object |
| `instance_segmentation.json` | `CInstanceSegmentationResult` | per_object |
| `pose_estimation.json` | `CPoseEstimationResult` | per_object |
| `monocular_depth.json` | `CMonocularDepthResult` | single |
| `semantic_segmentation.json` | `CSemanticSegmentationResult` | single |
| `vision_language.json` | `CVisionLanguageResult` | single |

`cardinality: "per_object"` means the result is a vector - one record per
detected thing, each with its own fields (`provides`). `cardinality: "single"`
means the whole frame produces exactly one record (a depth map, a seg map, an
embedding) - there is nothing to iterate per-object.

`provides` lists the real struct fields from the source header, flattened.
`source` points at the exact header/class/container so a field list here can
be checked against the real struct if the codebase changes.

These are inputs only (node A). None of them are things `gen_types.py`
generates code for - custom analytic blocks (node B, `kind:
"custom_analytic"`) still live in `ws_cur/workflows/*.json`.
