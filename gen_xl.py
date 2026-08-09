# ipoefgfefs SLM selection matrix generator
# SLM ONLY - anything that is not a small language model is out of the master sheet.
# cutoff used: generative language model, <= 16B dense params (or MoE with <4B active).
# removed models are kept on the Excluded sheet with the reason, nothing is silently dropped.
# every number carries a source tag in brackets.

import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HDR    = "BF0000"
GRP    = "1F2937"
FULL_G = "1A7F37"
ALLY_B = "0550AE"
COMM_O = "BC4C00"
OPEN_P = "6F42C1"
WARN   = "F5A623"
ALT    = "F6F8FA"
MUTED  = "6E7781"

thin = Side(style="thin", color="D0D7DE")
BORD = Border(left=thin, right=thin, top=thin, bottom=thin)

# llama.cpp quant spec, GB per billion params
QB = {"Q4_K_M": 0.56, "Q5_K_M": 0.69, "Q8_0": 1.06, "F16": 2.00}

ACC = {
    "Q4_K_M": "~-1.5% perplexity [LL: llama.cpp k-quants PR#1684]",
    "Q5_K_M": "~-0.6% perplexity [LL: llama.cpp k-quants PR#1684]",
    "Q8_0":   "~-0.04% perplexity [LL: llama.cpp k-quants PR#1684]",
    "F16":    "baseline (no loss)",
}

BW_GPU, BW_CPU = 1008.0, 80.0
EFF_G, EFF_C = 0.70, 0.60

def toks(size_gb, gpu=True):
    bw, eff = (BW_GPU, EFF_G) if gpu else (BW_CPU, EFF_C)
    return round(bw / size_gb * eff, 1)

def kv_gb(layers, kv_heads, head_dim, seq):
    # 2 (K and V) * layers * kv_heads * head_dim * seq * 2 bytes fp16
    return 2 * layers * kv_heads * head_dim * seq * 2 / (1024 ** 3)

COLS = [
    ("Model", 30), ("Developer", 20), ("Country", 12), ("License", 26),
    ("Compliance Tier", 14), ("SLM Class", 22), ("Task Category", 32),
    ("Params", 20), ("Quant / Precision", 14), ("File Size (GB)", 12),
    ("CPU RAM (GB)", 12), ("Max GPU VRAM @8K ctx (GB)", 16),
    ("Max GPU VRAM @Full ctx (GB)", 17), ("Context Window", 15),
    ("tok/s GPU (RTX 4090)", 14), ("tok/s CPU (x86 DDR5)", 14),
    ("ARM / Edge (Cortex-A53)", 20), ("Accuracy Impact vs F16", 34),
    ("Fine-Tune Method", 22), ("Min FT GPU (QLoRA)", 17),
    ("Inference Engines (official docs)", 46),
    ("Key Metric 1", 30), ("Key Metric 2", 26), ("Key Metric 3", 26),
    ("Metric Source", 46), ("Size / VRAM Source", 40), ("Notes for ipoefgfefs", 44),
]

TEXT_SLM  = "SLM - text only"
MM_SLM    = "SLM - multimodal (VLM)"
MOE_SLM   = "SLM - MoE (small active)"

# name dev country license tier slmclass task params ctx layers kv_heads head_dim fullseq params_B
# ft ftgpu engines m1 m2 m3 metric_source arm note
SLM = [
 dict(n="Qwen2.5-Coder 7B Instruct", d="Alibaba Cloud", c="China", l="Apache 2.0", t="OPEN",
   cls=TEXT_SLM, task="1. Code Gen C++ / FIM",
   p="7.6B dense", ctx="32K (128K YaRN)", ly=28, kvh=4, hd=128, full=32000, pb=7.6,
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, vLLM, SGLang, Ollama, TGI, MLX, TensorRT-LLM",
   m1="HumanEval 88.4%", m2="MultiPL-E C++ 63.4%", m3="MBPP 83.5%",
   ms="HumanEval [MB: qwenlm.github.io/blog/qwen2.5-coder]; C++ and MBPP [P: arxiv 2409.12186 Tbl 6]",
   arm="Not viable (4.4GB Q4)",
   note="RANK 1. Highest C++ score of any open model. 3x smaller than the 14b you run now."),
 dict(n="Phi-4 14B", d="Microsoft", c="US", l="MIT", t="FULL",
   cls=TEXT_SLM, task="2. Code Gen General, 6. Reasoning",
   p="14.7B dense", ctx="16K", ly=40, kvh=10, hd=128, full=16000, pb=14.7,
   ft="LoRA / QLoRA / Full", ftg="A10G 24GB",
   eng="llama.cpp, vLLM, Ollama, ONNX Runtime, TGI, MLX",
   m1="HumanEval 82.6%", m2="MMLU 84.8%", m3="MATH 80.4% / GSM8K 91.5%",
   ms="[P: arxiv 2412.08905 Tbl 2]",
   arm="Not viable (8.4GB Q4)",
   note="RANK 2. MIT + US origin = zero compliance argument. No FIM support."),
 dict(n="Granite 3.3 8B Instruct", d="IBM", c="US", l="Apache 2.0", t="FULL",
   cls=TEXT_SLM, task="1. Code Gen C++ / FIM, 6. Reasoning",
   p="8.1B dense", ctx="128K", ly=40, kvh=8, hd=128, full=128000, pb=8.1,
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, vLLM, Ollama, TGI, ONNX Runtime",
   m1="HumanEval 67.1%", m2="MMLU 65.5%", m3="FIM: YES",
   ms="[HF: ibm-granite/granite-3.3-8b-instruct model card]",
   arm="Not viable (4.6GB Q4)",
   note="Cleanest compliance story (US + Apache 2.0). Weakest C++ of the shortlist."),
 dict(n="Llama 3.1 8B Instruct", d="Meta", c="US", l="Llama 3.1 Community", t="FULL",
   cls=TEXT_SLM, task="2. Code Gen General, 6. Reasoning",
   p="8.0B dense", ctx="128K", ly=32, kvh=8, hd=128, full=128000, pb=8.0,
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, vLLM, SGLang, TensorRT-LLM, Ollama, TGI, MLX, ONNX Runtime",
   m1="HumanEval 72.6%", m2="MMLU 73.0%", m3="GSM8K 84.5%",
   ms="[P: arxiv 2407.21783 Tbl 16]",
   arm="Not viable (4.7GB Q4)",
   note="Widest engine support of any model here. Safe generalist fallback."),
 dict(n="StarCoder2 15B", d="BigCode (ServiceNow/HF/NVIDIA)", c="EU + US", l="BigCode OpenRAIL-M", t="ALLY",
   cls=TEXT_SLM + " (borderline 16B)", task="1. Code Gen C++ / FIM",
   p="16.0B dense - at the SLM ceiling", ctx="16K", ly=40, kvh=4, hd=128, full=16000, pb=16.0,
   ft="LoRA / QLoRA", ftg="A10G 24GB",
   eng="llama.cpp, vLLM, TGI, Ollama",
   m1="HumanEval 46.4%", m2="MultiPL-E C++ 41.4%", m3="FIM: YES (native)",
   ms="[P: arxiv 2402.19173 Tbl 12 and Tbl 14]",
   arm="Not viable (8.4GB Q4)",
   note="Base model, no instruct tuning. Strong FIM, poor instruction following."),
 dict(n="CodeGemma 7B IT", d="Google", c="US", l="Gemma Terms of Use", t="COMMERCIAL",
   cls=TEXT_SLM, task="1. Code Gen C++ / FIM",
   p="8.5B dense", ctx="8K", ly=28, kvh=16, hd=256, full=8192, pb=8.5,
   ft="LoRA", ftg="RTX 3060 12GB",
   eng="llama.cpp, Ollama, vLLM",
   m1="HumanEval 56.1%", m2="MultiPL-E C++: NA", m3="FIM: YES",
   ms="[MB: ai.google.dev/gemma/docs/codegemma/model_card]",
   arm="Not viable (5.0GB Q4)",
   note="WARNING 8K context. The ipoefgfefs prompt is 6-8K, leaving no room for output."),
 dict(n="Mistral 7B Instruct v0.3", d="Mistral AI", c="France", l="Apache 2.0", t="ALLY",
   cls=TEXT_SLM, task="2. Code Gen General",
   p="7.2B dense", ctx="32K", ly=32, kvh=8, hd=128, full=32000, pb=7.2,
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, vLLM, SGLang, Ollama, TGI, MLX, ONNX Runtime",
   m1="HumanEval 36.5% [LB: EvalPlus]", m2="MMLU 62.5%", m3="NA (no code benchmark in paper)",
   ms="MMLU [P: arxiv 2310.06825 Tbl 2]; HumanEval NOT in the paper [LB: evalplus.github.io/leaderboard]",
   arm="Not viable (4.1GB Q4)",
   note="General model, never code tuned. Too weak for C++ generation."),
 dict(n="Phi-3.5-mini 3.8B Instruct", d="Microsoft", c="US", l="MIT", t="FULL",
   cls=TEXT_SLM, task="2. Code Gen General, 6. Reasoning",
   p="3.8B dense", ctx="128K", ly=32, kvh=32, hd=96, full=128000, pb=3.8,
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, ONNX Runtime, Ollama, vLLM, MLX",
   m1="HumanEval 62.8%", m2="MMLU 69.0%", m3="GSM8K 86.2%",
   ms="[HF: microsoft/Phi-3.5-mini-instruct model card]",
   arm="Marginal (2.2GB Q4, ~4 tok/s)",
   note="Best accuracy per GB under 4B. No GQA, so KV cache is heavy at 128K."),
 dict(n="Llama 3.2 3B Instruct", d="Meta", c="US", l="Llama 3.2 Community", t="FULL",
   cls=TEXT_SLM, task="2. Code Gen General, 6. Reasoning",
   p="3.2B dense", ctx="128K", ly=28, kvh=8, hd=128, full=128000, pb=3.2,
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp (aarch64 NEON), ONNX Runtime, MLC-LLM, Ollama, ExecuTorch",
   m1="HumanEval 57.8%", m2="MMLU 63.4%", m3="GSM8K 77.7%",
   ms="[MB: ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices]",
   arm="YES - ~3.5 tok/s at Q4 (1.9GB)",
   note="EDGE CANDIDATE. Only text SLM here that runs on the Ambarella S50."),
 dict(n="Gemma 3 4B IT", d="Google", c="US", l="Gemma Terms of Use", t="COMMERCIAL",
   cls=MM_SLM, task="2. Code Gen General, 3. Image to Text",
   p="4.3B dense", ctx="128K", ly=34, kvh=4, hd=256, full=128000, pb=4.3,
   ft="LoRA / QLoRA", ftg="RTX 3060 12GB",
   eng="llama.cpp, Ollama, vLLM, MLX",
   m1="HumanEval 36.0%", m2="MMLU 59.6%", m3="Multimodal: YES (vision)",
   ms="[P: arxiv 2503.19786 Tbl 18]",
   arm="Marginal (2.5GB Q4)",
   note="Multimodal at 4B is rare, but C++ codegen is far too weak."),
 dict(n="DeepSeek-R1-Distill-Qwen-14B", d="DeepSeek", c="China", l="MIT", t="OPEN",
   cls=TEXT_SLM, task="6. Reasoning & Orchestration",
   p="14.8B dense", ctx="128K", ly=48, kvh=8, hd=128, full=128000, pb=14.8,
   ft="LoRA / QLoRA", ftg="A10G 24GB",
   eng="llama.cpp, vLLM, SGLang, Ollama",
   m1="MATH-500 93.9%", m2="AIME 2024 69.7%", m3="MMLU: NA (not reported)",
   ms="[P: arxiv 2501.12948 Tbl 5]",
   arm="Not viable (8.4GB Q4)",
   note="Chain-of-thought reasoner for Pass A. Verbose, slow for direct codegen."),
 dict(n="DeepSeek-Coder-V2-Lite Instruct", d="DeepSeek", c="China", l="DeepSeek License", t="OPEN",
   cls=MOE_SLM, task="1. Code Gen C++ (MoE)",
   p="15.7B MoE / 2.4B active", ctx="128K", ly=27, kvh=16, hd=128, full=128000, pb=15.7,
   ft="LoRA (MoE routing is fiddly)", ftg="A100 40GB",
   eng="llama.cpp, vLLM, SGLang",
   m1="HumanEval 81.1%", m2="MultiPL-E C++ 56.5%", m3="MBPP+ 68.8%",
   ms="[P: arxiv 2406.11931 Tbl 4]",
   arm="Not viable (9.0GB Q4)",
   note="MoE: only 2.4B active, so tok/s is roughly 6x a dense 15B."),
 # multimodal SLMs
 dict(n="Phi-3.5-Vision 4.2B", d="Microsoft", c="US", l="MIT", t="FULL",
   cls=MM_SLM, task="3. Image to Text",
   p="4.2B dense", ctx="128K", ly=32, kvh=32, hd=96, full=128000, pb=4.2,
   ft="LoRA", ftg="A10G 24GB",
   eng="llama.cpp, ONNX Runtime, vLLM, transformers",
   m1="MMBench 81.9%", m2="MMMU 43.0%", m3="TextVQA 72.0%",
   ms="[HF: microsoft/Phi-3.5-vision-instruct model card]",
   arm="Marginal (2.4GB Q4)",
   note="Best small VLM for camera frame captioning. MIT licensed."),
 dict(n="Qwen2-VL 7B Instruct", d="Alibaba Cloud", c="China", l="Apache 2.0", t="OPEN",
   cls=MM_SLM, task="3. Image to Text",
   p="8.3B dense", ctx="32K", ly=28, kvh=4, hd=128, full=32000, pb=8.3,
   ft="LoRA / Full", ftg="RTX 4090 24GB",
   eng="vLLM, SGLang, llama.cpp, transformers",
   m1="MMMU 54.1%", m2="DocVQA 94.5%", m3="MathVista 58.2%",
   ms="[P: arxiv 2409.12191 Tbl 3]",
   arm="Not viable (4.7GB Q4)",
   note="Best open VLM scores. Handles video frame sequences natively."),
 dict(n="Llama 3.2 11B Vision Instruct", d="Meta", c="US", l="Llama 3.2 Community", t="FULL",
   cls=MM_SLM, task="3. Image to Text",
   p="10.6B dense", ctx="128K", ly=40, kvh=8, hd=128, full=128000, pb=10.6,
   ft="LoRA", ftg="A10G 24GB",
   eng="vLLM, TGI, transformers, llama.cpp (vision path partial)",
   m1="MMMU 50.7%", m2="DocVQA 88.4%", m3="ChartQA 83.4%",
   ms="[MB: ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices]",
   arm="Not viable (7.9GB Q4)",
   note="US-origin VLM. llama.cpp vision support is still incomplete."),
 dict(n="InternVL2 8B", d="Shanghai AI Laboratory", c="China", l="MIT", t="OPEN",
   cls=MM_SLM, task="3. Image to Text",
   p="8.1B dense", ctx="8K", ly=32, kvh=8, hd=128, full=8192, pb=8.1,
   ft="LoRA", ftg="A10G 24GB",
   eng="LMDeploy, vLLM, transformers",
   m1="MMBench 81.7%", m2="MMMU 51.2%", m3="DocVQA 91.6%",
   ms="[MB: internvl.github.io / OpenCompass multimodal leaderboard]",
   arm="Not viable (4.6GB Q4)",
   note="MIT licensed. 8K context only."),
 dict(n="LLaVA-1.6 (NeXT) 13B", d="LLaVA team (UW-Madison / MSR)", c="US", l="Apache 2.0", t="FULL",
   cls=MM_SLM, task="3. Image to Text",
   p="13.4B dense", ctx="4K", ly=40, kvh=40, hd=128, full=4096, pb=13.4,
   ft="LoRA", ftg="A100 40GB",
   eng="llama.cpp, vLLM, SGLang, transformers",
   m1="MMBench 70.0%", m2="TextVQA 67.1%", m3="MMMU 35.9%",
   ms="[P: arxiv 2310.03744 Tbl 2]",
   arm="Not viable (7.4GB Q4)",
   note="Fully open Apache 2.0 VLM. Only 4K context."),
 dict(n="PaliGemma 3B mix-448", d="Google", c="US", l="Gemma Terms of Use", t="COMMERCIAL",
   cls=MM_SLM, task="3. Image to Text",
   p="2.9B dense", ctx="8K", ly=18, kvh=1, hd=256, full=8192, pb=2.9,
   ft="LoRA / Full", ftg="RTX 3090 24GB",
   eng="JAX, transformers, llama.cpp",
   m1="COCO CIDEr 141.9", m2="VQAv2 85.6%", m3="TextVQA 73.2%",
   ms="[P: arxiv 2407.07726 Tbl 4]",
   arm="Marginal (1.6GB Q4)",
   note="Built to be fine-tuned, weak zero-shot. MQA so KV cache is tiny."),
 dict(n="Moondream2 1.9B", d="Moondream (M87 Labs)", c="US", l="Apache 2.0", t="FULL",
   cls=MM_SLM, task="3. Image to Text",
   p="1.9B dense", ctx="2K", ly=24, kvh=32, hd=64, full=2048, pb=1.9,
   ft="LoRA", ftg="RTX 3060 12GB",
   eng="llama.cpp, ONNX Runtime, transformers",
   m1="VQAv2 79.4%", m2="TextVQA 60.2%", m3="DocVQA 61.9%",
   ms="[HF: vikhyatk/moondream2 model card]",
   arm="YES - ~4 img/s at Q4 (1.2GB)",
   note="EDGE VLM. Smallest usable image-to-text. Runs on the camera SoC."),
]

rows = []
for m in SLM:
    for q, mult in QB.items():
        fsz = round(m["pb"] * mult, 1)
        cpu = round(fsz * 1.15, 1)
        v8  = round(fsz + kv_gb(m["ly"], m["kvh"], m["hd"], 8192), 1)
        vf  = round(fsz + kv_gb(m["ly"], m["kvh"], m["hd"], m["full"]), 1)
        rows.append([
            m["n"], m["d"], m["c"], m["l"], m["t"], m["cls"], m["task"], m["p"],
            q, fsz, cpu, v8, vf, m["ctx"],
            toks(fsz, True), toks(fsz, False), m["arm"] if q == "Q4_K_M" else "NA (edge uses Q4 only)",
            ACC[q], m["ft"], m["ftg"], m["eng"],
            m["m1"], m["m2"], m["m3"], m["ms"],
            "[Calc: %s from llama.cpp quant spec; KV = 2*layers*kv_heads*head_dim*seq*2B, arch from paper or config.json]" % q,
            m["note"] if q == "Q4_K_M" else "",
        ])

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "SLM Matrix"

t = ws.cell(row=1, column=1,
    value="ipoefgfefs Workflow Builder - SLM Selection Matrix (small language models only, one row per quantization)")
t.font = Font(bold=True, size=13, color="FFFFFF")
t.fill = PatternFill("solid", fgColor=HDR)
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(COLS))
ws.row_dimensions[1].height = 24

for i, (h, w) in enumerate(COLS, start=1):
    c = ws.cell(row=2, column=i, value=h)
    c.font = Font(bold=True, size=9, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=GRP)
    c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    c.border = BORD
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[2].height = 40

TIER_C = {"FULL": FULL_G, "ALLY": ALLY_B, "COMMERCIAL": COMM_O, "OPEN": OPEN_P}
CLS_C  = {TEXT_SLM: "0A3069", MM_SLM: "6F42C1", MOE_SLM: "953800"}

r, last, band = 3, None, False
for row in rows:
    if row[0] != last:
        band = not band
        last = row[0]
    for j, v in enumerate(row, start=1):
        c = ws.cell(row=r, column=j, value=v)
        c.font = Font(size=9)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = BORD
        if band:
            c.fill = PatternFill("solid", fgColor=ALT)
        if j == 1:
            c.font = Font(size=9, bold=True)
        if j == 5:
            c.font = Font(size=9, bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=TIER_C.get(str(v), COMM_O))
            c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        if j == 6:
            key = str(v).split(" (")[0]
            c.font = Font(size=9, bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=CLS_C.get(key, GRP))
            c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        if j == 14 and str(v) in ("8K", "4K", "2K"):
            c.fill = PatternFill("solid", fgColor=WARN)
    r += 1

ws.freeze_panes = "B3"
ws.auto_filter.ref = "A2:%s%d" % (get_column_letter(len(COLS)), r - 1)


def sheet(name, title, headers, widths, data, bold_cols=(1,), tagcol=None, tagmap=None):
    s = wb.create_sheet(name)
    c = s.cell(row=1, column=1, value=title)
    c.font = Font(bold=True, size=12, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=HDR)
    s.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    for i, h in enumerate(headers, start=1):
        hc = s.cell(row=2, column=i, value=h)
        hc.font = Font(bold=True, size=10, color="FFFFFF")
        hc.fill = PatternFill("solid", fgColor=GRP)
        hc.alignment = Alignment(wrap_text=True, horizontal="center")
        hc.border = BORD
    for i, w in enumerate(widths, start=1):
        s.column_dimensions[get_column_letter(i)].width = w
    for i, rowv in enumerate(data, start=3):
        for j, v in enumerate(rowv, start=1):
            cc = s.cell(row=i, column=j, value=v)
            cc.font = Font(size=9, bold=(j in bold_cols))
            cc.alignment = Alignment(wrap_text=True, vertical="top")
            cc.border = BORD
            if tagcol and j == tagcol:
                cc.font = Font(size=9, bold=True, color="FFFFFF")
                cc.fill = PatternFill("solid", fgColor=(tagmap or {}).get(v, GRP))
                cc.alignment = Alignment(horizontal="center")
    return s


# --- what counts as an SLM ------------------------------------------------
sheet("SLM Definition",
 "What counts as an SLM in this matrix",
 ["Rule", "Applied as", "Why"],
 [40, 60, 70],
 [
  ("Must be a generative language model",
   "Has a tokenizer, a context window, and produces tokens",
   "Vision encoders, detectors, diffusion U-Nets and trackers output vectors, boxes or pixels. They are not language models and were removed."),
  ("Dense params <= 16B",
   "Phi-4 14B in. Devstral 24B, Codestral 22B, CodeLlama 34B, Qwen2.5 32B, Llama 3.3 70B out",
   "There is no formal SLM definition. The common cutoff is under 10B, stretched to ~15B. StarCoder2 15B is 16.0B and is flagged as borderline."),
  ("MoE judged on active params",
   "DeepSeek-Coder-V2-Lite in (15.7B total, 2.4B active). gpt-oss-20b out (21B total)",
   "MoE models are large on disk but small in compute. Kept where active params are under 4B."),
  ("Multimodal SLMs kept, labelled separately",
   "SLM Class column: text only / multimodal (VLM) / MoE",
   "A VLM is still a language model with a vision encoder attached. It generates text, so it stays - but it is not a candidate for C++ codegen."),
  ("Encoder-only models excluded",
   "BGE-M3, Nomic-Embed, all-MiniLM removed even though they process text",
   "No generation head. They emit an embedding vector, not tokens."),
 ], bold_cols=(1,))

# --- excluded --------------------------------------------------------------
EXC = [
 ("Devstral Small 24B","Language model, too large","23.6B dense - above the SLM ceiling","Was rank 3 for agentic multi-file codegen"),
 ("Codestral 22B","Language model, too large","22.2B dense, plus MNPL non-production licence","C++ codegen with FIM"),
 ("Mistral Small 3.1 24B","Language model, too large","24.0B dense","Pass A reasoning with vision"),
 ("CodeLlama 34B Instruct","Language model, too large","33.7B dense","C++ codegen"),
 ("Qwen2.5 32B Instruct","Language model, too large","32.5B dense","Pass A reasoning"),
 ("Llama 3.3 70B Instruct","Language model, too large","70.6B dense, needs 2x A100 at Q4","Highest accuracy option"),
 ("gpt-oss-20b","MoE, total params too large","21B total / 3.6B active - total is above the ceiling","US + Apache 2.0 reasoner"),
 ("CLIP, SigLIP, DINOv2, OpenCLIP, EVA-CLIP, MobileCLIP","Not a language model","Vision transformers, output a fixed embedding vector","Person and vehicle re-ID across cameras"),
 ("VideoMAE, VideoMAE V2, InternVideo2, X-CLIP, TimeSformer, VideoMamba","Not a language model","Spatiotemporal encoders, output a clip vector","Loitering, fall detection, intrusion"),
 ("BGE-M3, E5-Mistral-7B, GTE-Qwen2-7B, Nomic-Embed, all-MiniLM, Granite-Embedding","Not a language model (encoder only)","No generation head - emits an embedding, not tokens","Retrieval of C++ headers into the prompt"),
 ("Whisper (all sizes), Distil-Whisper, Parakeet, SenseVoice","Not a language model","Audio encoder-decoder, transcribes speech","Audio analytics from camera mics"),
 ("SDXL, SDXL-Turbo, FLUX.1-schnell, FLUX.1-dev, SD 1.5, SD 3.5","Not a language model","Diffusion U-Net / DiT denoisers, output pixels","Synthetic training data augmentation"),
 ("YOLOv8, YOLOv8m, YOLO11n, RT-DETR, RF-DETR, D-FINE","Not a language model","CNN and DETR detectors, output boxes","The analytics that custom_logic stitches together"),
 ("Grounding DINO, OWLv2","Not a language model","Has a text tower but does not generate text - outputs boxes","Open-vocabulary detection from a typed prompt"),
 ("OSNet, CLIP-ReID, ArcFace","Not a language model","Metric-learning networks, output an identity embedding","Multi-camera identity stitching"),
 ("ByteTrack, BoT-SORT","Not a model at all","Pure association algorithms - Kalman filter plus Hungarian matching, zero weights","Tracking, drops straight into the custom_logic C++"),
 ("Florence-2, GOT-OCR2.0, PaddleOCR v4, TrOCR, EasyOCR","Not a language model","Detector plus recognizer pipelines (CRNN / CTC)","LPR and text-in-frame reading"),
]
sheet("Excluded",
 "Removed from the matrix - what went and why (kept here so nothing is silently dropped)",
 ["Model(s)", "Reason removed", "Detail", "What it was for"],
 [52, 34, 60, 50], EXC, bold_cols=(1,))

# --- task categories -------------------------------------------------------
sheet("Task Categories",
 "Task categories present in the SLM matrix",
 ["Category", "What it does", "Relevant metrics only", "ipoefgfefs relevance"],
 [30, 50, 50, 50],
 [
  ("1. Code Gen C++","Generate compilable C++14 for the custom_logic block","HumanEval, MultiPL-E C++, MBPP, FIM support","PRIMARY - this is the core need"),
  ("2. Code Gen General","General programming, not C++ specialised","HumanEval, MBPP, MMLU","Fallback, and Pass A helper"),
  ("3. Image to Text","Describe a camera frame in natural language","MMBench, MMMU, DocVQA, TextVQA, COCO CIDEr","Scene summary blocks and alert text"),
  ("6. Reasoning & Orchestration","Pass A - build the IR / plan JSON from the workflow graph","MMLU, GSM8K, MATH, AIME","Decides which analytics to stitch and how"),
 ], bold_cols=(1,))

# --- inference engines (LLM serving only) ---------------------------------
ENG = [
 ("llama.cpp","ggml-org","MIT","GGUF Q2_K to Q8_0, F16","CPU and single GPU, edge deployment","Low - batch ~4, no paged attention","YES - aarch64 NEON native","CUDA sm_50+ (Maxwell), ROCm RDNA2+, Metal M1+, Vulkan, SYCL","[LL: github.com/ggml-org/llama.cpp build docs]"),
 ("llama-cpp-python","abetlen","MIT","GGUF (inherits llama.cpp)","Embedding in the Flask SRV layer","Low","YES","Inherits llama.cpp backends","[github.com/abetlen/llama-cpp-python]"),
 ("vLLM","vLLM project (UC Berkeley origin)","Apache 2.0","AWQ, GPTQ, FP8, INT8, BitsAndBytes","High-concurrency GPU serving","VERY HIGH - PagedAttention plus continuous batching","Partial (ARM GPU build experimental)","NVIDIA sm_70+ (Volta), AMD ROCm, Intel XPU, TPU","[P: arxiv 2309.06180 and docs.vllm.ai]"),
 ("SGLang","LMSYS","Apache 2.0","AWQ, GPTQ, FP8","Repeated prompt prefixes - the 6-8K C++ header block","VERY HIGH - RadixAttention prefix cache","No","NVIDIA sm_75+ (Turing), AMD ROCm","[P: arxiv 2312.07104 and docs.sglang.ai]"),
 ("TensorRT-LLM","NVIDIA","Apache 2.0","INT4/INT8 AWQ, FP8, NVFP4","Maximum NVIDIA throughput","VERY HIGH - in-flight batching","Jetson only","NVIDIA sm_75+ (Turing) only","[github.com/NVIDIA/TensorRT-LLM support matrix]"),
 ("Ollama","Ollama Inc.","MIT","GGUF (wraps llama.cpp)","Dev and prototyping - what you use today","Low","YES","Inherits llama.cpp backends","[ollama.com/docs]"),
 ("TGI","Hugging Face","Apache 2.0","AWQ, GPTQ, EETQ, bitsandbytes, FP8","Production Hugging Face stack","HIGH - continuous batching","Partial","NVIDIA sm_75+, AMD ROCm, Intel Gaudi, AWS Inferentia","[github.com/huggingface/text-generation-inference]"),
 ("ExLlamaV2","turboderp","MIT","EXL2 (2.0 to 8.0 bits, variable)","Fastest single consumer GPU","Medium","No","NVIDIA sm_60+ (Pascal), AMD ROCm","[github.com/turboderp/exllamav2]"),
 ("ONNX Runtime","Microsoft","MIT","INT8, INT4, FP16","Cross-platform, strong for Phi models","Medium","YES - aarch64 supported","CUDA, TensorRT, DirectML, OpenVINO, CoreML, NNAPI, QNN","[onnxruntime.ai/docs/execution-providers]"),
 ("MLC-LLM","MLC AI / CMU","Apache 2.0","q4f16_1, q3f16_1","Mobile and edge GPU","Low","YES","Vulkan, Metal, CUDA, OpenCL, WebGPU","[llm.mlc.ai/docs]"),
 ("LMDeploy","Shanghai AI Lab","Apache 2.0","AWQ, W4A16, KV cache INT8","InternVL and other VLM serving","HIGH","No","NVIDIA sm_70+","[github.com/InternLM/lmdeploy]"),
 ("MLX","Apple","MIT","4-bit, 8-bit","Apple Silicon dev machines","Low","YES (Apple Silicon)","Metal, M1 and later","[github.com/ml-explore/mlx]"),
 ("ExecuTorch","Meta","BSD-3","INT8, INT4","On-device Llama 3.2 3B","Low","YES","ARM CPU, Vulkan, CoreML, Qualcomm HTP","[pytorch.org/executorch]"),
]
sheet("Inference Engines",
 "Inference engines for SLM serving - support taken from official documentation",
 ["Engine","Vendor","License","Quantization support","Best for","Concurrency","ARM / aarch64","Hardware support (official docs)","Source"],
 [24, 28, 18, 34, 44, 40, 26, 48, 46], ENG, bold_cols=(1,))

# --- fine tuning -----------------------------------------------------------
FT = [
 ("Full fine-tune","~16x params (weights, grads, Adam states in FP32)","51 GB","61 GB","122 GB","224 GB","100% (reference)","[P: arxiv 2106.09685 LoRA paper Sec 4]"),
 ("LoRA (FP16 base)","~2.5x params","8 GB","10 GB","19 GB","35 GB","~97% of full FT","[P: arxiv 2106.09685 Tbl 2]"),
 ("QLoRA (NF4 base)","~1.2x params","4 GB","5 GB","10 GB","18 GB","~99% of full FT (matches 16-bit)","[P: arxiv 2305.14314 Tbl 4]"),
 ("DoRA","~1.5x params","5 GB","6 GB","12 GB","22 GB","~99.5% of full FT","[P: arxiv 2402.09353 Tbl 1]"),
 ("Spectrum","~1.5x params","5 GB","6 GB","12 GB","22 GB","~99% of full FT","[P: arxiv 2406.06623]"),
 ("Prompt tuning only","~1.0x params (inference footprint)","2 GB","2 GB","4 GB","8 GB","~85%, task dependent","[P: arxiv 2104.08691]"),
]
s4 = sheet("Fine-Tuning",
 "Fine-tuning methods - VRAM required across the SLM size range",
 ["Method","VRAM formula","3B","4B","8B","14B","Quality vs full FT","Source"],
 [24, 46, 12, 12, 12, 12, 30, 42], FT, bold_cols=(1,))
n = len(FT) + 4
s4.cell(row=n, column=1,
 value="ipoefgfefs Phase 2 plan: QLoRA on Qwen2.5-Coder 7B or Phi-4 14B, trained on custom_logic blocks harvested from Gate 3 smoke-test passes. 10-18 GB VRAM covers it - a single RTX 4090 or A10G is enough, no cluster needed."
 ).font = Font(size=9, italic=True)
s4.merge_cells(start_row=n, start_column=1, end_row=n, end_column=8)

# --- recommendation --------------------------------------------------------
REC = [
 ("1","Qwen2.5-Coder 7B Instruct","Apache 2.0","China","7.6B",
  "MultiPL-E C++ 63.4% - the highest C++ score of any open model, and the only shortlist entry where C++ was actually measured rather than inferred from Python. Half the size of the 14b in use today, and it has FIM for compile-retry patching.",
  "Q4_K_M 4.4 GB, 4.9 GB VRAM @8K","160 tok/s on RTX 4090",
  "China origin. If NDAA 889 is reinstated as a constraint this drops out and rank 2 becomes the pick."),
 ("2","Phi-4 14B","MIT","US","14.7B",
  "HumanEval 82.6%, MMLU 84.8%, MATH 80.4%. MIT plus US origin removes the compliance argument entirely. Same parameter count as the model you run now, so no infrastructure change.",
  "Q4_K_M 8.4 GB, 10.0 GB VRAM @8K","84 tok/s on RTX 4090",
  "No FIM support, and MultiPL-E C++ was never published for it - the C++ number is an inference from HumanEval."),
 ("3","Granite 3.3 8B Instruct","Apache 2.0","US","8.1B",
  "HumanEval 67.1% with native FIM, 128K context, and IBM indemnifies customers on training-data provenance. The safest choice if legal review is the bottleneck rather than accuracy.",
  "Q4_K_M 4.6 GB, 5.1 GB VRAM @8K","155 tok/s on RTX 4090",
  "Lowest C++ capability of the three. Expect more compile-retry iterations per block."),
]
s5 = sheet("Recommendation",
 "Final recommendation - replacing qwen2.5-coder:14b for the custom_logic C++ generator",
 ["Rank","Model","License","Country","Params","Why","Memory","Speed","Risk / caveat"],
 [7, 30, 16, 12, 12, 62, 28, 22, 46], REC, bold_cols=(1, 2))
for i in range(3, 3 + len(REC)):
    s5.row_dimensions[i].height = 78

n = len(REC) + 4
notes = [
 "Edge / on-camera (Ambarella S50, Cortex-A53):",
 "  Llama 3.2 3B Instruct is the only text SLM that fits - 1.9 GB at Q4, roughly 3.5 tok/s.",
 "  Moondream2 1.9B if you need image-to-text on the camera itself - 1.2 GB at Q4.",
 "",
 "Serving:",
 "  llama.cpp for the edge and the single-GPU path.",
 "  Move to SGLang on the server once concurrency matters - RadixAttention caches the shared",
 "  6-8K C++ header prefix across requests, which is exactly the shape of this prompt.",
 "",
 "Context window warning:",
 "  The ipoefgfefs prompt is 6-8K tokens. CodeGemma 7B (8K), InternVL2 8B (8K), PaliGemma (8K),",
 "  LLaVA-1.6 (4K) and Moondream2 (2K) leave little or no room for generated output.",
 "",
 "Note on scope:",
 "  This workbook now covers small language models only. The vision, video, embedding, ASR,",
 "  diffusion, detection, re-ID and OCR models that were previously included are listed on the",
 "  Excluded sheet with the reason - they are the analytics whose outputs custom_logic stitches",
 "  together, not candidates to replace the code generator.",
]
for k, line in enumerate(notes):
    c = s5.cell(row=n + k, column=1, value=line)
    c.font = Font(size=9, bold=(line.endswith(":")), name="Consolas")
    s5.merge_cells(start_row=n + k, start_column=1, end_row=n + k, end_column=9)

# --- references ------------------------------------------------------------
REFS = [
 ("P","HumanEval / Codex","Chen et al. 2021","https://arxiv.org/abs/2107.03374"),
 ("P","MultiPL-E (multi-language HumanEval incl. C++)","Cassano et al. 2022","https://arxiv.org/abs/2208.08227"),
 ("P","MBPP","Austin et al. 2021","https://arxiv.org/abs/2108.07732"),
 ("P","BigCodeBench","Zhuo et al. 2024","https://arxiv.org/abs/2406.15877"),
 ("P","MMLU","Hendrycks et al. 2020","https://arxiv.org/abs/2009.03300"),
 ("P","GSM8K","Cobbe et al. 2021","https://arxiv.org/abs/2110.14168"),
 ("P","MATH","Hendrycks et al. 2021","https://arxiv.org/abs/2103.03874"),
 ("P","MMMU","Yue et al. 2023","https://arxiv.org/abs/2311.16502"),
 ("P","TextVQA","Singh et al. 2019","https://arxiv.org/abs/1904.08920"),
 ("P","DocVQA","Mathew et al. 2020","https://arxiv.org/abs/2007.00398"),
 ("P","COCO Captions / CIDEr","Chen et al. 2015","https://arxiv.org/abs/1504.00325"),
 ("P","Phi-4","Abdin et al. 2024","https://arxiv.org/abs/2412.08905"),
 ("P","Phi-3 / Phi-3.5","Abdin et al. 2024","https://arxiv.org/abs/2404.14219"),
 ("P","Llama 3 herd of models","Grattafiori et al. 2024","https://arxiv.org/abs/2407.21783"),
 ("P","StarCoder2 and The Stack v2","Lozhkov et al. 2024","https://arxiv.org/abs/2402.19173"),
 ("P","Mistral 7B","Jiang et al. 2023","https://arxiv.org/abs/2310.06825"),
 ("P","Gemma 3","Gemma Team 2025","https://arxiv.org/abs/2503.19786"),
 ("P","Qwen2.5-Coder","Hui et al. 2024","https://arxiv.org/abs/2409.12186"),
 ("P","DeepSeek-Coder-V2","DeepSeek-AI 2024","https://arxiv.org/abs/2406.11931"),
 ("P","DeepSeek-R1 (distill results)","DeepSeek-AI 2025","https://arxiv.org/abs/2501.12948"),
 ("P","Qwen2-VL","Wang et al. 2024","https://arxiv.org/abs/2409.12191"),
 ("P","PaliGemma","Beyer et al. 2024","https://arxiv.org/abs/2407.07726"),
 ("P","LLaVA-1.5 / improved baselines","Liu et al. 2023","https://arxiv.org/abs/2310.03744"),
 ("P","LoRA","Hu et al. 2021","https://arxiv.org/abs/2106.09685"),
 ("P","QLoRA","Dettmers et al. 2023","https://arxiv.org/abs/2305.14314"),
 ("P","DoRA","Liu et al. 2024","https://arxiv.org/abs/2402.09353"),
 ("P","Spectrum","Hartford et al. 2024","https://arxiv.org/abs/2406.06623"),
 ("P","Prompt tuning","Lester et al. 2021","https://arxiv.org/abs/2104.08691"),
 ("P","vLLM / PagedAttention","Kwon et al. 2023","https://arxiv.org/abs/2309.06180"),
 ("P","SGLang / RadixAttention","Zheng et al. 2023","https://arxiv.org/abs/2312.07104"),
 ("MB","Llama 3.2 blog (3B and 11B Vision)","Meta 2024","https://ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices/"),
 ("MB","Qwen2.5-Coder blog","Alibaba 2024","https://qwenlm.github.io/blog/qwen2.5-coder/"),
 ("MB","CodeGemma model card","Google 2024","https://ai.google.dev/gemma/docs/codegemma/model_card"),
 ("MB","InternVL","Shanghai AI Lab","https://internvl.github.io/"),
 ("HF","Granite 3.3 8B Instruct card","IBM","https://huggingface.co/ibm-granite/granite-3.3-8b-instruct"),
 ("HF","Phi-3.5-mini card","Microsoft","https://huggingface.co/microsoft/Phi-3.5-mini-instruct"),
 ("HF","Phi-3.5-vision card","Microsoft","https://huggingface.co/microsoft/Phi-3.5-vision-instruct"),
 ("HF","Moondream2 card","Moondream","https://huggingface.co/vikhyatk/moondream2"),
 ("LB","EvalPlus leaderboard (HumanEval+ / MBPP+)","EvalPlus","https://evalplus.github.io/leaderboard.html"),
 ("LB","BigCode Models leaderboard","BigCode","https://huggingface.co/spaces/bigcode/bigcode-models-leaderboard"),
 ("LB","OpenCompass multimodal leaderboard","Shanghai AI Lab","https://rank.opencompass.org.cn/leaderboard-multimodal"),
 ("LL","llama.cpp repo (quant spec, hardware backends)","ggml-org","https://github.com/ggml-org/llama.cpp"),
 ("LL","llama.cpp k-quants PR #1684 (perplexity deltas)","ggml-org","https://github.com/ggml-org/llama.cpp/pull/1684"),
 ("IE","vLLM docs","vLLM","https://docs.vllm.ai/"),
 ("IE","SGLang docs","LMSYS","https://docs.sglang.ai/"),
 ("IE","TensorRT-LLM support matrix","NVIDIA","https://github.com/NVIDIA/TensorRT-LLM"),
 ("IE","ONNX Runtime execution providers","Microsoft","https://onnxruntime.ai/docs/execution-providers/"),
 ("IE","LMDeploy","Shanghai AI Lab","https://github.com/InternLM/lmdeploy"),
 ("IE","MLC-LLM docs","MLC AI","https://llm.mlc.ai/docs/"),
 ("IE","ExecuTorch","Meta","https://pytorch.org/executorch/"),
 ("CM","NDAA Section 889 text","US Congress","https://www.acquisition.gov/far/52.204-25"),
 ("CM","Apache License 2.0","Apache Foundation","https://www.apache.org/licenses/LICENSE-2.0"),
 ("CM","Llama 3.x Community License","Meta","https://www.llama.com/llama3_3/license/"),
 ("CM","Gemma Terms of Use","Google","https://ai.google.dev/gemma/terms"),
 ("CM","BigCode OpenRAIL-M","BigCode","https://www.bigcode-project.org/docs/pages/model-license/"),
 ("CM","DeepSeek Model License","DeepSeek","https://github.com/deepseek-ai/DeepSeek-LLM/blob/main/LICENSE-MODEL"),
]
TAGC = {"P": FULL_G, "MB": ALLY_B, "HF": COMM_O, "LB": OPEN_P, "LL": "24292F", "IE": "24292F", "CM": HDR}
s6 = sheet("References",
 "References - every source cited in this workbook",
 ["Tag","What it covers","Author / org","Link"],
 [8, 56, 34, 74], REFS, bold_cols=(), tagcol=1, tagmap=TAGC)
for i in range(3, 3 + len(REFS)):
    s6.cell(row=i, column=4).font = Font(size=9, color="0550AE", underline="single")
n = len(REFS) + 4
s6.cell(row=n, column=1,
 value="Tag key:  P = peer-reviewed paper   MB = official model blog or announcement   HF = HuggingFace model card   "
       "LB = public leaderboard (no paper exists for the number)   LL = llama.cpp family docs   "
       "IE = inference engine docs   CM = compliance or licence text"
 ).font = Font(size=9, italic=True)
s6.merge_cells(start_row=n, start_column=1, end_row=n, end_column=4)

OUT = "/home/h412581/Downloads/ipoefgfefs_SLM_Matrix.xlsx"
wb.save(OUT)
print("saved:", OUT)
print("models:", len(SLM), " rows:", len(rows))
for s in wb.sheetnames:
    print("  sheet:", s)
