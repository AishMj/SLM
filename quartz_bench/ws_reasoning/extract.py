#!/usr/bin/env python3
"""raw model output -> just the function body(ies), with any echoed struct
or #include we already generated stripped out. Models routinely echo back
part or all of what they were shown - this is not an error, it is normal
completion behaviour, same as ws_cur's README notes for its own model."""
import re, sys

RESERVED_STRUCTS = {"Box", "Point2f", "InRecord", "OutRecord", "Config"}


def strip_think(raw):
    """DeepSeek-R1-Distill answers with a <think>...</think> reasoning trace
    before the real answer. Keep only what comes after it - same rule the
    model's own chat template applies."""
    if "</think>" in raw:
        return raw.split("</think>", 1)[1]
    return raw


def generated_only(raw):
    """Everything after the last prompt-echo line and before the stats
    footer - i.e. just what the model actually generated this call, with
    llama-cli's own echo of our prompt stripped out."""
    lines = raw.splitlines()
    buf = []
    for line in lines:
        if line.startswith("> "):
            buf = []
            continue
        if line.startswith("[ Prompt:"):
            break
        buf.append(line)
    return "\n".join(buf)


def think_truncated(raw):
    """True if this was a <think>-first model (we appended '<think>\\n' to
    every prompt) that never reached '</think>' - it ran out of its token
    budget still reasoning. Distinct from a bad-code compile failure: the
    fix is more budget, not 'here is what's wrong with your C++'."""
    gen = generated_only(raw)
    return len(gen.strip()) > 0 and "</think>" not in gen


def strip_fence(raw):
    m = re.search(r"```(?:cpp)?\n(.*?)```", raw, re.DOTALL)
    if m:
        return m.group(1)
    return generated_only(raw)


def strip_echoed_types(src):
    src = re.sub(r'#include\s*["<][^">]+[">]\s*\n', "", src)
    out_lines = []
    i = 0
    lines = src.splitlines()
    while i < len(lines):
        line = lines[i]
        m = re.match(r"\s*struct\s+(\w+)", line)
        if m and m.group(1) in RESERVED_STRUCTS:
            depth = line.count("{") - line.count("}")
            i += 1
            while i < len(lines) and depth > 0:
                depth += lines[i].count("{") - lines[i].count("}")
                i += 1
            continue
        out_lines.append(line)
        i += 1
    return "\n".join(out_lines)


def is_stub(body):
    """True if the function has no real statement - just braces/comments/
    whitespace. Compiles fine, never fires, so it's a rejected answer."""
    no_comments = re.sub(r"//.*", "", body)
    no_comments = re.sub(r"/\*.*?\*/", "", no_comments, flags=re.DOTALL)
    core = re.sub(r"[{}\s;]", "", no_comments)
    # drop the function signature itself (name + params), keep only body-ish text
    core = re.sub(r"\bvoid\s+\w+\([^)]*\)", "", core)
    return len(core) == 0


if __name__ == "__main__":
    raw = sys.stdin.read()
    raw = strip_think(raw)
    body = strip_fence(raw)
    body = strip_echoed_types(body)
    body = body.replace("<|im_end|>", "").replace("<｜end▁of▁sentence｜>", "")
    sys.stdout.write(body.strip() + "\n")
