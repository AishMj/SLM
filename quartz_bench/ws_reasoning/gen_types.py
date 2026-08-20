#!/usr/bin/env python3
"""workflow.json -> the C++ this pair actually needs, and nothing else.

No fixed contract.hpp. Every struct here is built from the field names two
nodes actually declare (provides / requires_fields / params), so it only
ever contains what this specific A->B pair uses.

Case, derived from node kind (see README.md):
  ai task   -> custom   : this function IS block B's implementation.
                          in  = A.provides (filtered to B.requires_fields)
                          out = B.spec.provides
  custom    -> ai task  : adapts a custom result into the next task's input.
                          NOT YET SUPPORTED - the registry has no input shape
                          for an ai task node to adapt into.
  ai task   -> ai task  : same gap as above.
"""
import json, pathlib

# field name -> (C++ type, default init). The only vocabulary this maps is
# the field names already used across tasks.json / vellum_registry blocks.
FIELD_CPP = {
    "bbox":          ("Box", "Box()"),
    "class_id":      ("int32_t", "0"),
    "confidence":    ("float", "0.0f"),
    "label":         ("std::string", "std::string()"),
    "track_id":      ("int32_t", "-1"),
    "track_ids":     ("std::vector<int32_t>", "{}"),
    "person_count":  ("int32_t", "0"),
    "timestamp_us":  ("int64_t", "0"),
    "camera_id":     ("std::string", "std::string()"),
    "direction":     ("std::string", "std::string()"),
    "use_case":      ("std::string", "std::string()"),
}

PARAM_TYPE_REMAP = {
    "SPt2f": "Point2f",
    "std::vector<SPt2f>": "std::vector<Point2f>",
}


class UnsupportedEdge(Exception):
    pass


def load(wf_path):
    return json.loads(pathlib.Path(wf_path).read_text())


def _node(wf, node_id):
    return next(n for n in wf["nodes"] if n["id"] == node_id)


def classify(wf):
    a = _node(wf, wf["edges"][0]["from"])
    b = _node(wf, wf["edges"][0]["to"])
    a_custom = a.get("kind") == "custom_analytic"
    b_custom = b.get("kind") == "custom_analytic"
    if not a_custom and b_custom:
        return "task_to_custom", a, b
    if a_custom and not b_custom:
        raise UnsupportedEdge(
            "custom -> ai task: the registry has no declared input shape "
            "for an ai task node, so there is nothing to adapt into yet.")
    if not a_custom and not b_custom:
        raise UnsupportedEdge(
            "ai task -> ai task: same gap - no declared input shape on "
            "the downstream task node.")
    raise UnsupportedEdge("custom -> custom: not a modelled case yet.")


def _struct(name, fields):
    lines = [f"struct {name} {{"]
    for f in fields:
        cpp_t, default = FIELD_CPP[f]
        lines.append(f"    {cpp_t} {f} = {default};")
    lines.append("};")
    return "\n".join(lines)


def _param_type(t):
    return PARAM_TYPE_REMAP.get(t, t)


def build(wf_path):
    """Returns dict: case, fn_name, header (str), signature (str),
    in_fields, out_fields, param_fields, frames."""
    wf = load(wf_path)
    case, a, b = classify(wf)
    spec = b["spec"]

    in_fields = [f for f in spec["requires_fields"]]
    out_fields = spec["provides"]
    params = spec.get("params", {})
    frames = spec["frames"]
    fn_name = f"custom_logic_{a['type']}_{b['type']}"

    # timestamp_us/camera_id are frame-level, not per-detection - they were
    # never in any node's provides/requires_fields, yet a custom block's
    # output almost always needs them. Rather than let the model invent or
    # misattribute them (it did, repeatedly), pass the frame's real values
    # in as explicit arguments.
    frame_ctx_fields = [f for f in ("timestamp_us", "camera_id")
                         if f in out_fields and f not in in_fields]

    need_box = "bbox" in in_fields or "bbox" in out_fields
    need_pt = any(_param_type(t).replace("std::vector<", "").rstrip(">") == "Point2f"
                  for t in params.values())

    parts = []
    if need_box:
        parts.append("struct Box { float x=0, y=0, w=0, h=0; };")
    if need_pt:
        parts.append("struct Point2f { float x=0, y=0; };")
    parts.append(_struct("InRecord", in_fields))
    parts.append(_struct("OutRecord", out_fields))
    if params:
        lines = ["struct Config {"]
        for name, t in params.items():
            lines.append(f"    {_param_type(t)} {name};")
        lines.append("};")
        parts.append("\n".join(lines))

    header = "\n\n".join(parts)

    def _ctx_arg(f):
        cpp_t = FIELD_CPP[f][0]
        return f", const {cpp_t} &{f}" if cpp_t == "std::string" else f", {cpp_t} {f}"

    ctx_args = "".join(_ctx_arg(f) for f in frame_ctx_fields)
    if frames == "2":
        sig = (f"void {fn_name}(const std::vector<InRecord> &prev,\n"
               f"                const std::vector<InRecord> &curr{ctx_args},\n"
               f"                const Config &cfg, std::vector<OutRecord> &out)")
    else:
        sig = (f"void {fn_name}(const std::vector<InRecord> &curr{ctx_args},\n"
               f"                const Config &cfg, std::vector<OutRecord> &out)")

    return {
        "case": case, "fn_name": fn_name, "header": header, "signature": sig,
        "in_fields": in_fields, "out_fields": out_fields,
        "param_fields": params, "frames": frames,
        "a_type": a["type"], "b_type": b["type"],
        "frame_ctx_fields": frame_ctx_fields,
    }


def write_header(wf_path, out_path):
    info = build(wf_path)
    text = ("#pragma once\n"
            "#include <cstdint>\n"
            "#include <string>\n"
            "#include <vector>\n\n"
            f"{info['header']}\n")
    pathlib.Path(out_path).write_text(text)
    return info


if __name__ == "__main__":
    import sys
    info = build(sys.argv[1])
    print(info["header"])
    print()
    print(info["signature"])
