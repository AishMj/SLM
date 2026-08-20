#!/usr/bin/env python3
"""workflow.json -> prompt.txt. Nothing hand-written per pair - not even a
task description. The TASK section is assembled from the workflow.json's own
fields: the block's name, what it is chained after, and the field shapes on
each side. The model infers what to build from the name alone.

No rule, no skeleton, no helper allow-list, no fixed contract.hpp. Types are
generated per pair by gen_types.py from workflow.json, so the model only
ever sees the fields THIS A->B edge actually uses.
"""
import os, pathlib, sys
import gen_types

TEMPLATE = os.environ.get("TEMPLATE", "chatml")


def _wrap(user_text):
    if TEMPLATE == "deepseek":
        # DeepSeek-R1-Distill uses <|User|>/<|Assistant|> tokens, no system
        # role wrapper, and expects <think>\n to trigger its reasoning trace.
        return f"<｜User｜>{SYSTEM}\n\n{user_text}<｜Assistant｜><think>\n"
    return "\n\n".join([
        "<|im_start|>user", SYSTEM, user_text,
        "<|im_end|>\n<|im_start|>assistant\n",
    ])

SYSTEM = """You write C++14 for a video analytics pipeline.

RULES
  1. Use only the struct fields shown below. Never redefine a type. Never
     read a field from a struct that does not declare it - check the struct
     definition, not what a field "should" logically have.
  2. Compare object classes on class_id, an integer, if you use it at all.
  3. Fill every OutRecord field that is meaningful for what you push.
  4. Construct each OutRecord field-by-field:
       OutRecord r;
       r.some_field = ...;
       out.push_back(r);
     Do not use brace-init (OutRecord{a, b, c}) - a value in the wrong slot
     is a silent bug there, an obvious one here.
  5. No #include, unless your logic genuinely needs OpenCV or nlohmann/json,
     in which case you may add exactly one of:
       #include <opencv2/opencv.hpp>
       #include "nlohmann/json.hpp"
     Do not add either speculatively.
  6. No main, no printf, no cout, no exceptions, no new/delete/malloc. Call
     no function that was not declared for you.
  7. Push nothing to out when the condition is not met.

Nobody is going to give you an algorithm or a rule. Work out the correct
logic yourself, from the block's name and the fields available to you.

OUTPUT
  The complete function: signature plus body. No explanation, no markdown
  fences."""


def _task(info):
    parts = [
        f"Implement the custom analytic block \"{info['b_type']}\". "
        f"It runs immediately after \"{info['a_type']}\", which supplies "
        f"one InRecord per detection, with fields: "
        f"{', '.join(info['in_fields'])}.",

        f"InRecord has ONLY these fields: {', '.join(info['in_fields'])}. "
        f"Nothing else - no timestamp, no camera id, no other field. Do not "
        f"read a field from InRecord that is not in that list.",
    ]
    if info["frame_ctx_fields"]:
        parts.append(
            f"{' and '.join(info['frame_ctx_fields'])} for the current frame "
            f"{'are' if len(info['frame_ctx_fields']) > 1 else 'is'} given to "
            f"you directly as function parameters - use "
            f"{'those' if len(info['frame_ctx_fields']) > 1 else 'it'}, do "
            f"not invent {'them' if len(info['frame_ctx_fields']) > 1 else 'it'} "
            f"or read {'them' if len(info['frame_ctx_fields']) > 1 else 'it'} "
            f"from InRecord.")
    parts.append(
        f"For each condition your \"{info['b_type']}\" logic decides has "
        f"occurred, push one OutRecord with fields: "
        f"{', '.join(info['out_fields'])}.")
    return "\n\n".join(parts)


def build(wf_path):
    info = gen_types.build(wf_path)
    user = f"""TYPES FOR THIS TASK - do not redefine, do not #include:

{info['header']}

TASK
  {_task(info)}

Write this function:

{info['signature']}

Output the complete function - signature, opening brace, body, closing
brace. Nothing else."""

    return _wrap(user)


def build_fix(wf_path, prev_code, error_log):
    info = gen_types.build(wf_path)
    user = f"""TYPES FOR THIS TASK - do not redefine, do not #include:

{info['header']}

Your previous answer failed to compile.

PREVIOUS CODE
```cpp
{prev_code}
```

COMPILER ERROR
```
{error_log}
```

Fix it. Same rules as before: only the struct fields above, only the two
optional includes if truly needed, no other includes, no explanation. You
have a limited token budget - reason briefly, then write the code.
Output the whole corrected function, signature included:

{info['signature']}"""

    return _wrap(user)


def build_truncated(wf_path):
    """Previous attempt ran out of its token budget mid-reasoning and never
    reached an answer. Not a code bug - ask again with an explicit push to
    stop reasoning and commit to an answer quickly."""
    info = gen_types.build(wf_path)
    user = f"""TYPES FOR THIS TASK - do not redefine, do not #include:

{info['header']}

TASK
  {_task(info)}

Your previous attempt ran out of space while still reasoning and never
produced an answer. This time: think briefly, then commit to an answer.
Do not second-guess yourself at length - write the function as soon as you
have a plausible approach.

Write this function:

{info['signature']}

Output the complete function - signature, opening brace, body, closing
brace. Nothing else."""

    return _wrap(user)


def build_empty(wf_path, prev_code):
    info = gen_types.build(wf_path)
    user = f"""TYPES FOR THIS TASK - do not redefine, do not #include:

{info['header']}

TASK
  {_task(info)}

Your previous answer compiled but contained no real logic - just a comment
placeholder. That is not an acceptable answer: it never pushes to out, so it
can never fire. Write the actual logic this time. You have a limited token
budget - reason briefly, then write the code.

PREVIOUS (rejected) ANSWER
```cpp
{prev_code}
```

Output the complete function - signature, opening brace, body, closing
brace. Nothing else:

{info['signature']}"""

    return _wrap(user)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "empty":
        wf_path, code_path = sys.argv[2], sys.argv[3]
        sys.stdout.write(build_empty(wf_path, pathlib.Path(code_path).read_text()))
    elif mode == "truncated":
        sys.stdout.write(build_truncated(sys.argv[2]))
    elif mode == "fix":
        wf_path, code_path, err_path = sys.argv[2], sys.argv[3], sys.argv[4]
        sys.stdout.write(build_fix(wf_path,
                                    pathlib.Path(code_path).read_text(),
                                    pathlib.Path(err_path).read_text()))
    else:
        sys.stdout.write(build(sys.argv[1]))
