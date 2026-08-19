#!/usr/bin/env python3
"""workflow.json -> prompt.txt. Nothing is hand-written; every line comes from
the workflow file or the shared contract."""
import json, sys, pathlib

COMMON = pathlib.Path(__file__).resolve().parent.parent / "common"

SYSTEM = """You write C++14 for a video analytics pipeline. You produce ONE function.

HARD RULES
  1. Use only the types given below. Never redefine one.
  2. Call only the functions on the allow-list. Never invent a function name.
  3. Use only the libraries listed. If none, C++14 standard library only.
  4. Compare object classes on class_id, never on the label string.
  5. Fill EVERY field of the output event that the block must provide.
  6. No #include, no main, no printf, no cout, no exceptions, no new/delete.
  7. Return without pushing anything when the condition is not met.

OUTPUT
  Only the body of the function and its closing brace. No explanation.
  No markdown fences."""

ALLOW = """FUNCTIONS YOU MAY CALL - nothing else exists:
  bool  pointInZone(float x, float y, const std::vector<SPt2f> &poly);
  float sideOfLine(const SPt2f &a, const SPt2f &b, float px, float py);
  float boxOverlap(const SBox &a, const SBox &b);   // percent of a covered, 0..100
  SBox  headRegion(const SBox &person, float ratio);

CONSTANTS THAT EXIST:
  const int CLASS_PERSON = 0;  CLASS_BICYCLE = 1;  CLASS_VEHICLE = 2;"""


def types_section():
    txt = (COMMON / "contract.hpp").read_text()
    keep, on = [], False
    for line in txt.splitlines():
        if line.startswith("struct S") or line.startswith("struct C"):
            on = True
        if on:
            keep.append(line)
        if on and line.startswith("};"):
            on = False
    return "TYPES THAT ALREADY EXIST - do not redefine, do not #include:\n\n" + "\n".join(keep)


def build(wf_path):
    wf = json.loads(pathlib.Path(wf_path).read_text())
    A = next(n for n in wf["nodes"] if not n.get("generate_code"))
    B = next(n for n in wf["nodes"] if n.get("generate_code"))
    s = B["spec"]

    libs = ", ".join(s["libraries"]) if s["libraries"] else "none - C++14 standard library only"

    block = f"""THIS BLOCK

  name           : {B['type']}
  input event    : {A['type']}
  input semantic : {A['emits']}
  input provides : {', '.join(A['provides'])}
  output semantic: {s['emits']}
  must fill      : {', '.join(s['provides'])}
  frames         : {s['frames']}
  libraries      : {libs}
  params         : {', '.join(s['params'].keys())}

RULE
  {s['rule']}"""

    skeleton = (COMMON / "templates" / s["skeleton"]).read_text().rstrip()

    return "\n\n".join([
        "<|im_start|>user",
        SYSTEM, types_section(), ALLOW, block,
        "COMPLETE THIS FUNCTION. Output only the body and the closing brace.\n\n" + skeleton + "\n    // ZZBEGINZZ",
        "<|im_end|>\n<|im_start|>assistant\n",
    ])


if __name__ == "__main__":
    sys.stdout.write(build(sys.argv[1]))
