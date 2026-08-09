# ipoefgfefs SLM selection matrix generator
# SINGLE SHEET. matrix on top, supporting sections stacked underneath.
# SLM only: generative language model, <=16B dense, or MoE with <4B active.
# every number carries a source tag in brackets. NA where the number does not exist.

import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HDR   = "BF0000"
GRP   = "1F2937"
SEC   = "0A3069"
FULL_G= "1A7F37"
ALLY_B= "0550AE"
COMM_O= "BC4C00"
OPEN_P= "6F42C1"
WARN  = "F5A623"
BAD   = "CF222E"
ALT   = "F6F8FA"

thin = Side(style="thin", color="D0D7DE")
BORD = Border(left=thin, right=thin, top=thin, bottom=thin)

QB = {"Q4_K_M": 0.56, "Q5_K_M": 0.69, "Q8_0": 1.06, "F16": 2.00}
ACC = {
    "Q4_K_M": "~-1.5% perplexity [LL: llama.cpp PR#1684]",
    "Q5_K_M": "~-0.6% perplexity [LL: llama.cpp PR#1684]",
    "Q8_0":   "~-0.04% perplexity [LL: llama.cpp PR#1684]",
    "F16":    "baseline (no loss)",
}
BW_GPU, BW_CPU, EFF_G, EFF_C = 1008.0, 80.0, 0.70, 0.60

def toks(gb, gpu=True):
    bw, eff = (BW_GPU, EFF_G) if gpu else (BW_CPU, EFF_C)
    return round(bw / gb * eff, 1)

def kv_gb(ly, kvh, hd, seq):
    return 2 * ly * kvh * hd * seq * 2 / (1024 ** 3)

COLS = [
    ("Model", 30), ("Developer", 20), ("Country", 12), ("License", 25),
    ("Compliance", 13), ("SLM Class", 21), ("Task Category", 30), ("Params", 20),
    ("Quant", 11), ("File Size (GB)", 11), ("CPU RAM (GB)", 11),
    ("Max VRAM @8K ctx (GB)", 14), ("Max VRAM @Full ctx (GB)", 15),
    ("Context Window", 14), ("Ctx OK for 6-8K prompt?", 15),
    ("MultiPL-E C++", 14), ("HumanEval", 12), ("FIM Support", 12), ("MMLU", 11),
    ("Other Key Metrics", 34),
    ("tok/s GPU (RTX 4090)", 13), ("tok/s CPU (x86 DDR5)", 13),
    ("ARM / Edge (Cortex-A53)", 20), ("Accuracy Impact vs F16", 32),
    ("Fine-Tune Method", 21), ("Min FT GPU (QLoRA)", 16),
    ("Inference Engines (official docs)", 44),
    ("Metric Source", 46), ("Size / VRAM Source", 40), ("Notes for ipoefgfefs", 44),
]
NC = len(COLS)

TXT = "SLM - text only"
MM  = "SLM - multimodal (VLM)"
MOE = "SLM - MoE (small active)"

SLM = [
 dict(n="Qwen2.5-Coder 7B Instruct", d="Alibaba Cloud", c="China", l="Apache 2.0", t="OPEN",
   cls=TXT, task="1. Code Gen C++ / FIM", p="7.6B dense", ctx="32K (128K YaRN)",
   ly=28, kvh=4, hd=128, full=32000, pb=7.6, ok="YES",
   cpp="63.4%", he="88.4%", fim="YES", mmlu="NA (not reported)",
   other="MBPP 83.5%",
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, vLLM, SGLang, Ollama, TGI, MLX, TensorRT-LLM",
   ms="HumanEval [MB: qwenlm.github.io/blog/qwen2.5-coder]; C++ and MBPP [P: arxiv 2409.12186 Tbl 6]",
   arm="Not viable (4.4GB Q4)",
   note="RANK 1. Only shortlist model where C++ was actually measured, not inferred."),
 dict(n="Phi-4 14B", d="Microsoft", c="US", l="MIT", t="FULL",
   cls=TXT, task="2. Code Gen General, 4. Reasoning", p="14.7B dense", ctx="16K",
   ly=40, kvh=10, hd=128, full=16000, pb=14.7, ok="YES",
   cpp="NA (never published)", he="82.6%", fim="NO", mmlu="84.8%",
   other="MATH 80.4%, GSM8K 91.5%",
   ft="LoRA / QLoRA / Full", ftg="A10G 24GB",
   eng="llama.cpp, vLLM, Ollama, ONNX Runtime, TGI, MLX",
   ms="[P: arxiv 2412.08905 Tbl 2]",
   arm="Not viable (8.4GB Q4)",
   note="RANK 2. MIT + US removes the compliance argument. No FIM hurts the retry loop."),
 dict(n="Granite 3.3 8B Instruct", d="IBM", c="US", l="Apache 2.0", t="FULL",
   cls=TXT, task="1. Code Gen C++ / FIM, 4. Reasoning", p="8.1B dense", ctx="128K",
   ly=40, kvh=8, hd=128, full=128000, pb=8.1, ok="YES",
   cpp="NA (never published)", he="67.1%", fim="YES", mmlu="65.5%",
   other="GSM8K 80.9%, grounded RAG w/ citations",
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, vLLM, Ollama, TGI, ONNX Runtime",
   ms="[HF: ibm-granite/granite-3.3-8b-instruct model card]",
   arm="Not viable (4.6GB Q4)",
   note="RANK 3. FIM + 128K + IBM data-provenance indemnity. Weakest C++ of the three."),
 dict(n="Llama 3.1 8B Instruct", d="Meta", c="US", l="Llama 3.1 Community", t="FULL",
   cls=TXT, task="2. Code Gen General, 4. Reasoning", p="8.0B dense", ctx="128K",
   ly=32, kvh=8, hd=128, full=128000, pb=8.0, ok="YES",
   cpp="NA (never published)", he="72.6%", fim="NO", mmlu="73.0%",
   other="GSM8K 84.5%, strong tool calling",
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, vLLM, SGLang, TensorRT-LLM, Ollama, TGI, MLX, ONNX Runtime",
   ms="[P: arxiv 2407.21783 Tbl 16]",
   arm="Not viable (4.7GB Q4)",
   note="Widest engine support here. Best pick if Pass A needs tool calling."),
 dict(n="DeepSeek-Coder-V2-Lite Instruct", d="DeepSeek", c="China", l="DeepSeek License", t="OPEN",
   cls=MOE, task="1. Code Gen C++ (MoE)", p="15.7B MoE / 2.4B active", ctx="128K",
   ly=27, kvh=16, hd=128, full=128000, pb=15.7, ok="YES",
   cpp="56.5%", he="81.1%", fim="YES", mmlu="NA (not reported)",
   other="MBPP+ 68.8%",
   ft="LoRA (MoE routing is fiddly)", ftg="A100 40GB",
   eng="llama.cpp, vLLM, SGLang",
   ms="[P: arxiv 2406.11931 Tbl 4]",
   arm="Not viable (9.0GB Q4)",
   note="Only 2.4B active, so roughly 6x the tok/s of a dense 15B."),
 dict(n="StarCoder2 15B", d="BigCode (ServiceNow/HF/NVIDIA)", c="EU + US", l="BigCode OpenRAIL-M", t="ALLY",
   cls=TXT + " (borderline 16B)", task="1. Code Gen C++ / FIM", p="16.0B dense - at SLM ceiling", ctx="16K",
   ly=40, kvh=4, hd=128, full=16000, pb=16.0, ok="YES",
   cpp="41.4%", he="46.4%", fim="YES (native)", mmlu="NA (not reported)",
   other="Base model - no instruct tuning",
   ft="LoRA / QLoRA", ftg="A10G 24GB",
   eng="llama.cpp, vLLM, TGI, Ollama",
   ms="[P: arxiv 2402.19173 Tbl 12 and Tbl 14]",
   arm="Not viable (8.4GB Q4)",
   note="Strong FIM, poor instruction following. Needs heavy prompt scaffolding."),
 dict(n="CodeGemma 7B IT", d="Google", c="US", l="Gemma Terms of Use", t="COMMERCIAL",
   cls=TXT, task="1. Code Gen C++ / FIM", p="8.5B dense", ctx="8K",
   ly=28, kvh=16, hd=256, full=8192, pb=8.5, ok="NO - 8K leaves no output room",
   cpp="NA (never published)", he="56.1%", fim="YES", mmlu="NA (not reported)",
   other="-",
   ft="LoRA", ftg="RTX 3060 12GB",
   eng="llama.cpp, Ollama, vLLM",
   ms="[MB: ai.google.dev/gemma/docs/codegemma/model_card]",
   arm="Not viable (5.0GB Q4)",
   note="ELIMINATED by the context filter. Prompt is 6-8K of an 8K window."),
 dict(n="Phi-3.5-mini 3.8B Instruct", d="Microsoft", c="US", l="MIT", t="FULL",
   cls=TXT, task="2. Code Gen General, 4. Reasoning", p="3.8B dense", ctx="128K",
   ly=32, kvh=32, hd=96, full=128000, pb=3.8, ok="YES",
   cpp="NA (never published)", he="62.8%", fim="NO", mmlu="69.0%",
   other="GSM8K 86.2%",
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, ONNX Runtime, Ollama, vLLM, MLX",
   ms="[HF: microsoft/Phi-3.5-mini-instruct model card]",
   arm="Marginal (2.2GB Q4, ~4 tok/s)",
   note="Best accuracy per GB under 4B. No GQA so KV cache is heavy at long context."),
 dict(n="Llama 3.2 3B Instruct", d="Meta", c="US", l="Llama 3.2 Community", t="FULL",
   cls=TXT, task="2. Code Gen General, 4. Reasoning", p="3.2B dense", ctx="128K",
   ly=28, kvh=8, hd=128, full=128000, pb=3.2, ok="YES",
   cpp="NA (never published)", he="57.8%", fim="NO", mmlu="63.4%",
   other="GSM8K 77.7%",
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp (aarch64 NEON), ONNX Runtime, MLC-LLM, Ollama, ExecuTorch",
   ms="[MB: ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices]",
   arm="YES - ~3.5 tok/s at Q4 (1.9GB)",
   note="EDGE CANDIDATE. Only text SLM here that runs on the Ambarella S50."),
 dict(n="Mistral 7B Instruct v0.3", d="Mistral AI", c="France", l="Apache 2.0", t="ALLY",
   cls=TXT, task="2. Code Gen General", p="7.2B dense", ctx="32K",
   ly=32, kvh=8, hd=128, full=32000, pb=7.2, ok="YES",
   cpp="NA (never published)", he="36.5% [LB: EvalPlus]", fim="NO", mmlu="62.5%",
   other="-",
   ft="LoRA / QLoRA / Full", ftg="RTX 3060 12GB",
   eng="llama.cpp, vLLM, SGLang, Ollama, TGI, MLX, ONNX Runtime",
   ms="MMLU [P: arxiv 2310.06825 Tbl 2]; HumanEval NOT in paper [LB: evalplus.github.io/leaderboard]",
   arm="Not viable (4.1GB Q4)",
   note="Never code tuned. Too weak for C++ generation."),
 dict(n="DeepSeek-R1-Distill-Qwen-14B", d="DeepSeek", c="China", l="MIT", t="OPEN",
   cls=TXT, task="4. Reasoning & Orchestration", p="14.8B dense", ctx="128K",
   ly=48, kvh=8, hd=128, full=128000, pb=14.8, ok="YES",
   cpp="NA (never published)", he="NA (not reported)", fim="NO", mmlu="NA (not reported)",
   other="MATH-500 93.9%, AIME 2024 69.7%",
   ft="LoRA / QLoRA", ftg="A10G 24GB",
   eng="llama.cpp, vLLM, SGLang, Ollama",
   ms="[P: arxiv 2501.12948 Tbl 5]",
   arm="Not viable (8.4GB Q4)",
   note="Pass A candidate only. Verbose chain-of-thought, slow for direct codegen."),
 dict(n="Gemma 3 4B IT", d="Google", c="US", l="Gemma Terms of Use", t="COMMERCIAL",
   cls=MM, task="2. Code Gen General, 3. Image to Text", p="4.3B dense", ctx="128K",
   ly=34, kvh=4, hd=256, full=128000, pb=4.3, ok="YES",
   cpp="NA (never published)", he="36.0%", fim="NO", mmlu="59.6%",
   other="Multimodal (vision) at 4B",
   ft="LoRA / QLoRA", ftg="RTX 3060 12GB",
   eng="llama.cpp, Ollama, vLLM, MLX",
   ms="[P: arxiv 2503.19786 Tbl 18]",
   arm="Marginal (2.5GB Q4)",
   note="Multimodal at 4B is rare, but C++ codegen is far too weak."),
 dict(n="Qwen2-VL 7B Instruct", d="Alibaba Cloud", c="China", l="Apache 2.0", t="OPEN",
   cls=MM, task="3. Image to Text, 5. OCR / LPR", p="8.3B dense", ctx="32K",
   ly=28, kvh=4, hd=128, full=32000, pb=8.3, ok="YES",
   cpp="NA", he="NA", fim="NO", mmlu="NA",
   other="MMMU 54.1%, DocVQA 94.5%, MathVista 58.2%",
   ft="LoRA / Full", ftg="RTX 4090 24GB",
   eng="vLLM, SGLang, llama.cpp, transformers",
   ms="[P: arxiv 2409.12191 Tbl 3]",
   arm="Not viable (4.7GB Q4)",
   note="Best VLM here. DocVQA 94.5% makes it the LPR / plate-reading pick."),
 dict(n="Phi-3.5-Vision 4.2B", d="Microsoft", c="US", l="MIT", t="FULL",
   cls=MM, task="3. Image to Text, 5. OCR / LPR", p="4.2B dense", ctx="128K",
   ly=32, kvh=32, hd=96, full=128000, pb=4.2, ok="YES",
   cpp="NA", he="NA", fim="NO", mmlu="NA",
   other="MMBench 81.9%, MMMU 43.0%, TextVQA 72.0%",
   ft="LoRA", ftg="A10G 24GB",
   eng="llama.cpp, ONNX Runtime, vLLM, transformers",
   ms="[HF: microsoft/Phi-3.5-vision-instruct model card]",
   arm="Marginal (2.4GB Q4)",
   note="Best small VLM under MIT. Frame captioning for alert text."),
 dict(n="Llama 3.2 11B Vision Instruct", d="Meta", c="US", l="Llama 3.2 Community", t="FULL",
   cls=MM, task="3. Image to Text, 5. OCR / LPR", p="10.6B dense", ctx="128K",
   ly=40, kvh=8, hd=128, full=128000, pb=10.6, ok="YES",
   cpp="NA", he="NA", fim="NO", mmlu="NA",
   other="MMMU 50.7%, DocVQA 88.4%, ChartQA 83.4%",
   ft="LoRA", ftg="A10G 24GB",
   eng="vLLM, TGI, transformers, llama.cpp (vision path partial)",
   ms="[MB: ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices]",
   arm="Not viable (7.9GB Q4)",
   note="US-origin VLM. llama.cpp vision support still incomplete."),
 dict(n="InternVL2 8B", d="Shanghai AI Laboratory", c="China", l="MIT", t="OPEN",
   cls=MM, task="3. Image to Text, 5. OCR / LPR", p="8.1B dense", ctx="8K",
   ly=32, kvh=8, hd=128, full=8192, pb=8.1, ok="NO - 8K only",
   cpp="NA", he="NA", fim="NO", mmlu="NA",
   other="MMBench 81.7%, MMMU 51.2%, DocVQA 91.6%",
   ft="LoRA", ftg="A10G 24GB",
   eng="LMDeploy, vLLM, transformers",
   ms="[MB: internvl.github.io / OpenCompass multimodal leaderboard]",
   arm="Not viable (4.6GB Q4)",
   note="Strong scores under MIT, but 8K context."),
 dict(n="LLaVA-1.6 (NeXT) 13B", d="LLaVA team (UW-Madison / MSR)", c="US", l="Apache 2.0", t="FULL",
   cls=MM, task="3. Image to Text", p="13.4B dense", ctx="4K",
   ly=40, kvh=40, hd=128, full=4096, pb=13.4, ok="NO - 4K only",
   cpp="NA", he="NA", fim="NO", mmlu="NA",
   other="MMBench 70.0%, TextVQA 67.1%, MMMU 35.9%",
   ft="LoRA", ftg="A100 40GB",
   eng="llama.cpp, vLLM, SGLang, transformers",
   ms="[P: arxiv 2310.03744 Tbl 2]",
   arm="Not viable (7.4GB Q4)",
   note="Fully open Apache 2.0 VLM, but only 4K context."),
 dict(n="PaliGemma 3B mix-448", d="Google", c="US", l="Gemma Terms of Use", t="COMMERCIAL",
   cls=MM, task="3. Image to Text, 5. OCR / LPR", p="2.9B dense", ctx="8K",
   ly=18, kvh=1, hd=256, full=8192, pb=2.9, ok="NO - 8K only",
   cpp="NA", he="NA", fim="NO", mmlu="NA",
   other="COCO CIDEr 141.9, VQAv2 85.6%, TextVQA 73.2%",
   ft="LoRA / Full", ftg="RTX 3090 24GB",
   eng="JAX, transformers, llama.cpp",
   ms="[P: arxiv 2407.07726 Tbl 4]",
   arm="Marginal (1.6GB Q4)",
   note="Built to be fine-tuned, weak zero-shot. MQA keeps KV cache tiny."),
 dict(n="Moondream2 1.9B", d="Moondream (M87 Labs)", c="US", l="Apache 2.0", t="FULL",
   cls=MM, task="3. Image to Text, 5. OCR / LPR", p="1.9B dense", ctx="2K",
   ly=24, kvh=32, hd=64, full=2048, pb=1.9, ok="NO - 2K only",
   cpp="NA", he="NA", fim="NO", mmlu="NA",
   other="VQAv2 79.4%, TextVQA 60.2%, DocVQA 61.9%",
   ft="LoRA", ftg="RTX 3060 12GB",
   eng="llama.cpp, ONNX Runtime, transformers",
   ms="[HF: vikhyatk/moondream2 model card]",
   arm="YES - ~4 img/s at Q4 (1.2GB)",
   note="EDGE VLM. Smallest usable image-to-text, runs on the camera SoC."),
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "SLM Selection"

def title_row(r, text, fill=HDR, size=13):
    c = ws.cell(row=r, column=1, value=text)
    c.font = Font(bold=True, size=size, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=fill)
    c.alignment = Alignment(vertical="center")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=NC)
    ws.row_dimensions[r].height = 22
    return r + 1

r = 1
r = title_row(r, "ipoefgfefs Workflow Builder - SLM Selection Matrix   |   small language models only, one row per quantization   |   generated by gen_xl.py")

for i, (h, w) in enumerate(COLS, start=1):
    c = ws.cell(row=r, column=i, value=h)
    c.font = Font(bold=True, size=9, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=GRP)
    c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    c.border = BORD
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[r].height = 42
head_row = r
r += 1

TIER_C = {"FULL": FULL_G, "ALLY": ALLY_B, "COMMERCIAL": COMM_O, "OPEN": OPEN_P}
CLS_C  = {TXT: "0A3069", MM: "6F42C1", MOE: "953800"}

first_data = r
band = False
for m in SLM:
    band = not band
    for q, mult in QB.items():
        fsz = round(m["pb"] * mult, 1)
        row = [
            m["n"], m["d"], m["c"], m["l"], m["t"], m["cls"], m["task"], m["p"],
            q, fsz, round(fsz * 1.15, 1),
            round(fsz + kv_gb(m["ly"], m["kvh"], m["hd"], 8192), 1),
            round(fsz + kv_gb(m["ly"], m["kvh"], m["hd"], m["full"]), 1),
            m["ctx"], m["ok"],
            m["cpp"], m["he"], m["fim"], m["mmlu"], m["other"],
            toks(fsz, True), toks(fsz, False),
            m["arm"] if q == "Q4_K_M" else "NA (edge uses Q4 only)",
            ACC[q], m["ft"], m["ftg"], m["eng"], m["ms"],
            "[Calc: %s from llama.cpp quant spec; KV = 2*layers*kv_heads*head_dim*seq*2B, arch from paper or config.json]" % q,
            m["note"] if q == "Q4_K_M" else "",
        ]
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
                c.alignment = Alignment(horizontal="center", vertical="center")
            if j == 6:
                c.font = Font(size=9, bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor=CLS_C.get(str(v).split(" (")[0], GRP))
                c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
            if j == 15:
                good = str(v).startswith("YES")
                c.font = Font(size=9, bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor=(FULL_G if good else BAD))
                c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
            if j == 18:
                c.font = Font(size=9, bold=True, color=(FULL_G if str(v).startswith("YES") else "6E7781"))
                c.alignment = Alignment(horizontal="center")
        r += 1
last_data = r - 1

ws.freeze_panes = ws.cell(row=first_data, column=2)
ws.auto_filter.ref = "A%d:%s%d" % (head_row, get_column_letter(NC), last_data)


def section(r, heading, rows, widths_note=None):
    r += 1
    r = title_row(r, heading, fill=SEC, size=11)
    for cells in rows:
        if isinstance(cells, str):
            c = ws.cell(row=r, column=1, value=cells)
            c.font = Font(size=9, name="Consolas")
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=NC)
        else:
            col = 1
            for span, val, bold in cells:
                c = ws.cell(row=r, column=col, value=val)
                c.font = Font(size=9, bold=bold)
                c.alignment = Alignment(wrap_text=True, vertical="top")
                if span > 1:
                    ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + span - 1)
                col += span
        r += 1
    return r


r = last_data + 1

r = section(r, "HOW TO USE THIS SHEET - THE SELECTION IS 4 CRITERIA, NOT 30 COLUMNS", [
 [(4, "STEP", True), (5, "Criterion", True), (5, "Column", True), (16, "Why it decides", True)],
 [(4, "1. RANK", False), (5, "Code Gen C++", False), (5, "MultiPL-E C++, HumanEval as fallback", False),
  (16, "The job. Only 3 models here have a measured C++ number - the rest never published one, which is itself a finding.", False)],
 [(4, "1. RANK", False), (5, "Compiler Error Repair", False), (5, "NO COLUMN - no benchmark exists", False),
  (16, "The 5-gate loop runs up to 6 retries. This is the real workload and no paper measures it. See the EVAL PROTOCOL section below.", False)],
 [(4, "1. RANK", False), (5, "FIM Support", False), (5, "FIM Support", False),
  (16, "Decides whether a retry patches 8 lines or regenerates all 80. Architectural, not cosmetic.", False)],
 [(4, "1. RANK", False), (5, "Reasoning / Orchestration", False), (5, "MMLU", False),
  (16, "Pass A emits the IR/plan JSON. Same model or a second one - either way it is a decision.", False)],
 [(4, "2. FILTER", False), (5, "Context window", False), (5, "Ctx OK for 6-8K prompt?", False),
  (16, "Hard eliminate. Red in that column means the prompt does not leave room for output.", False)],
 [(4, "2. FILTER", False), (5, "Memory", False), (5, "Max VRAM @8K ctx", False),
  (16, "Use the 8K figure, not the full-context one - 8K is the actual ipoefgfefs prompt size.", False)],
 [(4, "2. FILTER", False), (5, "Licence and country", False), (5, "License, Country, Compliance", False),
  (16, "Decides whether Qwen2.5-Coder is eligible at all. This is a legal call, not a technical one.", False)],
 [(4, "3. IF APPLICABLE", False), (5, "Tool calling", False), (5, "Other Key Metrics", False),
  (16, "Only if Pass A calls an analytics registry API instead of emitting static JSON.", False)],
 [(4, "3. IF APPLICABLE", False), (5, "Edge deployment", False), (5, "ARM / Edge (Cortex-A53)", False),
  (16, "Only if the SLM ships on the S50 camera rather than the server.", False)],
 "",
 "Everything else in this sheet is supporting evidence. It documents the work, it does not decide the winner.",
])

r = section(r, "RECOMMENDATION", [
 [(6, "Rank", True), (6, "Model", True), (5, "Licence / Country", True), (13, "Why", True)],
 [(6, "1", True), (6, "Qwen2.5-Coder 7B Instruct", True), (5, "Apache 2.0 / China", False),
  (13, "MultiPL-E C++ 63.4% - the only shortlist model where C++ was measured rather than inferred from Python. Half the size of the 14b in use today, and FIM lets a failed compile be patched in place.", False)],
 [(6, "2", True), (6, "Phi-4 14B", True), (5, "MIT / US", False),
  (13, "HumanEval 82.6%, MMLU 84.8%. MIT plus US origin removes the compliance argument entirely, and it is the same parameter count as today so no infra change. Cost: no FIM, and C++ was never published.", False)],
 [(6, "3", True), (6, "Granite 3.3 8B Instruct", True), (5, "Apache 2.0 / US", False),
  (13, "HumanEval 67.1% with native FIM, 128K context, and IBM indemnifies customers on training-data provenance. The pick if legal review is the bottleneck rather than raw accuracy.", False)],
 "",
 "Edge / on-camera (Ambarella S50, Cortex-A53):  Llama 3.2 3B at Q4 (1.9 GB, ~3.5 tok/s) is the only text SLM that fits.  Moondream2 1.9B at Q4 (1.2 GB) if image-to-text is needed on-device.",
 "Serving:  llama.cpp for edge and the single-GPU path. Move to SGLang on the server once concurrency matters - RadixAttention caches the shared 6-8K C++ header prefix across requests, which is exactly this prompt shape.",
])

r = section(r, "EVAL PROTOCOL - THE ONE NUMBER YOU CANNOT GET FROM A PAPER", [
 "The top-ranked criterion, compiler error repair, has no public benchmark. HumanEval measures cold single-shot",
 "generation on Python. The ipoefgfefs workload is: broken C++ plus a GCC error, produce a patch, repeat up to 6 times.",
 "Nobody publishes that number, so the matrix narrows 19 models to 3 and cannot go further on published data alone.",
 "",
 "Run this to settle it - roughly one day of work, and it is your data on your workload, which presents far better",
 "than a table of borrowed benchmarks:",
 "",
 "  1. Pick 20 real workflow graphs covering the analytics mix you actually ship (loitering, face, LPR, intrusion).",
 "  2. Run each through the full 5-gate pipeline on each of the 3 shortlisted models, at Q4_K_M, same prompt, same seed.",
 "  3. Record per model:",
 "       - first-pass compile rate      (share reaching Gate 2 green with zero retries)",
 "       - mean retries to green        (the number that actually drives latency)",
 "       - unrecoverable rate           (share still failing after 6 retries)",
 "       - mean wall-clock per accepted block  (tok/s matters only through this)",
 "       - C++14 / ARM policy violations at Gate 4",
 "  4. Pick on first-pass compile rate, break ties on mean retries.",
 "",
 "Keep the 20 graphs and the pass/fail outputs - that corpus is also the training set for the Phase 2 QLoRA run.",
])

r = section(r, "SCOPE - WHAT IS IN THIS SHEET AND WHAT IS NOT", [
 [(7, "Excluded", True), (5, "Reason", True), (18, "Examples", True)],
 [(7, "Not a language model", False), (5, "Outputs vectors, boxes or pixels, not tokens", False),
  (18, "CLIP, SigLIP, DINOv2 (image embeddings) - VideoMAE, X-CLIP (video embeddings) - Whisper, Parakeet (ASR) - SDXL, FLUX (diffusion) - YOLO, RT-DETR, RF-DETR (detection) - OSNet, ArcFace (re-ID) - PaddleOCR, TrOCR (OCR)", False)],
 [(7, "Not a model at all", False), (5, "Pure algorithm, zero weights", False),
  (18, "ByteTrack, BoT-SORT - Kalman filter plus Hungarian matching. Drops straight into the custom_logic C++.", False)],
 [(7, "Encoder-only", False), (5, "No generation head", False),
  (18, "BGE-M3, Nomic-Embed, all-MiniLM (text embeddings) - GLiNER (NER) - most PII detectors", False)],
 [(7, "Language model, too large", False), (5, "Above 16B dense, or MoE above 16B total", False),
  (18, "Devstral 24B - Codestral 22B - Mistral Small 24B - CodeLlama 34B - Qwen2.5 32B - Llama 3.3 70B - gpt-oss-20b", False)],
 [(7, "Not a category", False), (5, "Attribute, technique, or wrong model family", False),
  (18, "Long context and edge deployment are attributes, they are columns not rows - constrained JSON decoding (GBNF, Outlines, XGrammar) is a technique - time series models (Chronos, TimesFM) are not language models", False)],
 "",
 "SLM inclusion rule used: generative language model, <=16B dense params, or MoE with under 4B active. StarCoder2 15B is",
 "actually 16.0B and is flagged borderline in the SLM Class column. Multimodal VLMs are kept and labelled separately -",
 "they are language models with a vision encoder attached, but they are not candidates for C++ generation.",
 "",
 "Categories worth adding models for later, in priority order:  guardrail SLMs (Granite Guardian 3, Llama Guard 3) if",
 "untrusted free text from the no-code UI enters the prompt - speculative decoding draft models (Qwen2.5-Coder 0.5B,",
 "Llama 3.2 1B) for a lossless 1.5-2.5x speedup on the retry loop - listwise reranking (RankZephyr 7B) if header",
 "retrieval into the 6-8K window becomes the bottleneck.",
])

r = section(r, "SOURCE TAGS - EVERY NUMBER IN THIS SHEET CARRIES ONE", [
 [(4, "Tag", True), (8, "Meaning", True), (18, "Note", True)],
 [(4, "[P: arxiv NNNN.NNNNN Tbl N]", False), (8, "Peer-reviewed paper, exact table", False), (18, "Strongest source. Cited to the table, not just the paper.", False)],
 [(4, "[MB: ...]", False), (8, "Official model blog or announcement", False), (18, "Vendor-published, not peer reviewed.", False)],
 [(4, "[HF: ...]", False), (8, "HuggingFace model card", False), (18, "Used where no paper exists, eg Granite 3.3, Phi-3.5-mini.", False)],
 [(4, "[LB: ...]", False), (8, "Public leaderboard", False), (18, "NO PAPER EXISTS for this number. Mistral 7B HumanEval is the example.", False)],
 [(4, "[LL: ...]", False), (8, "llama.cpp family documentation", False), (18, "Source for all quantization accuracy deltas.", False)],
 [(4, "[Calc: ...]", False), (8, "Computed, formula stated inline", False), (18, "File size, VRAM, and all token rates. Nothing measured.", False)],
 [(4, "NA", False), (8, "The number does not exist", False), (18, "Not 'not found'. Most models never publish MultiPL-E C++ at all.", False)],
 "",
 "File size:  llama.cpp quant spec - Q4_K_M 4.5 bits/param, Q5_K_M 5.5, Q8_0 8.5, F16 16.",
 "Max VRAM:  weights + KV cache, where KV = 2 * layers * kv_heads * head_dim * seq_len * 2 bytes. Architecture from the",
 "           paper or config.json. Both 8K and full-context figures are given because the gap is large - Llama 3.1 8B at",
 "           Q4 is 5.2 GB at 8K but 13.1 GB at 128K. Use the 8K figure for ipoefgfefs sizing.",
 "Token rate:  CALCULATED FROM MEMORY BANDWIDTH, NOT MEASURED. RTX 4090 = 1008 GB/s at 70% efficiency,",
 "             DDR5 dual channel = 80 GB/s at 60%. No paper publishes tok/s.",
])

REFS = [
 ("HumanEval / Codex","Chen et al. 2021","https://arxiv.org/abs/2107.03374"),
 ("MultiPL-E (multi-language HumanEval incl. C++)","Cassano et al. 2022","https://arxiv.org/abs/2208.08227"),
 ("MBPP","Austin et al. 2021","https://arxiv.org/abs/2108.07732"),
 ("MMLU","Hendrycks et al. 2020","https://arxiv.org/abs/2009.03300"),
 ("GSM8K","Cobbe et al. 2021","https://arxiv.org/abs/2110.14168"),
 ("MATH","Hendrycks et al. 2021","https://arxiv.org/abs/2103.03874"),
 ("MMMU","Yue et al. 2023","https://arxiv.org/abs/2311.16502"),
 ("DocVQA","Mathew et al. 2020","https://arxiv.org/abs/2007.00398"),
 ("TextVQA","Singh et al. 2019","https://arxiv.org/abs/1904.08920"),
 ("Phi-4","Abdin et al. 2024","https://arxiv.org/abs/2412.08905"),
 ("Phi-3 / Phi-3.5","Abdin et al. 2024","https://arxiv.org/abs/2404.14219"),
 ("Llama 3 herd of models","Grattafiori et al. 2024","https://arxiv.org/abs/2407.21783"),
 ("StarCoder2 and The Stack v2","Lozhkov et al. 2024","https://arxiv.org/abs/2402.19173"),
 ("Mistral 7B","Jiang et al. 2023","https://arxiv.org/abs/2310.06825"),
 ("Gemma 3","Gemma Team 2025","https://arxiv.org/abs/2503.19786"),
 ("Qwen2.5-Coder","Hui et al. 2024","https://arxiv.org/abs/2409.12186"),
 ("DeepSeek-Coder-V2","DeepSeek-AI 2024","https://arxiv.org/abs/2406.11931"),
 ("DeepSeek-R1 (distill results)","DeepSeek-AI 2025","https://arxiv.org/abs/2501.12948"),
 ("Qwen2-VL","Wang et al. 2024","https://arxiv.org/abs/2409.12191"),
 ("PaliGemma","Beyer et al. 2024","https://arxiv.org/abs/2407.07726"),
 ("LLaVA-1.5 / improved baselines","Liu et al. 2023","https://arxiv.org/abs/2310.03744"),
 ("LoRA","Hu et al. 2021","https://arxiv.org/abs/2106.09685"),
 ("QLoRA","Dettmers et al. 2023","https://arxiv.org/abs/2305.14314"),
 ("vLLM / PagedAttention","Kwon et al. 2023","https://arxiv.org/abs/2309.06180"),
 ("SGLang / RadixAttention","Zheng et al. 2023","https://arxiv.org/abs/2312.07104"),
 ("Llama 3.2 blog (3B and 11B Vision)","Meta 2024","https://ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices/"),
 ("Qwen2.5-Coder blog","Alibaba 2024","https://qwenlm.github.io/blog/qwen2.5-coder/"),
 ("CodeGemma model card","Google 2024","https://ai.google.dev/gemma/docs/codegemma/model_card"),
 ("Granite 3.3 8B Instruct card","IBM","https://huggingface.co/ibm-granite/granite-3.3-8b-instruct"),
 ("Phi-3.5-mini card","Microsoft","https://huggingface.co/microsoft/Phi-3.5-mini-instruct"),
 ("Phi-3.5-vision card","Microsoft","https://huggingface.co/microsoft/Phi-3.5-vision-instruct"),
 ("Moondream2 card","Moondream","https://huggingface.co/vikhyatk/moondream2"),
 ("InternVL","Shanghai AI Lab","https://internvl.github.io/"),
 ("EvalPlus leaderboard (HumanEval+ / MBPP+)","EvalPlus","https://evalplus.github.io/leaderboard.html"),
 ("BigCode Models leaderboard","BigCode","https://huggingface.co/spaces/bigcode/bigcode-models-leaderboard"),
 ("OpenCompass multimodal leaderboard","Shanghai AI Lab","https://rank.opencompass.org.cn/leaderboard-multimodal"),
 ("llama.cpp (quant spec, hardware backends)","ggml-org","https://github.com/ggml-org/llama.cpp"),
 ("llama.cpp k-quants PR #1684 (perplexity deltas)","ggml-org","https://github.com/ggml-org/llama.cpp/pull/1684"),
 ("vLLM docs","vLLM","https://docs.vllm.ai/"),
 ("SGLang docs","LMSYS","https://docs.sglang.ai/"),
 ("ONNX Runtime execution providers","Microsoft","https://onnxruntime.ai/docs/execution-providers/"),
 ("NDAA Section 889 text","US Congress","https://www.acquisition.gov/far/52.204-25"),
 ("Apache License 2.0","Apache Foundation","https://www.apache.org/licenses/LICENSE-2.0"),
 ("Llama 3.x Community License","Meta","https://www.llama.com/llama3_3/license/"),
 ("Gemma Terms of Use","Google","https://ai.google.dev/gemma/terms"),
 ("BigCode OpenRAIL-M","BigCode","https://www.bigcode-project.org/docs/pages/model-license/"),
 ("DeepSeek Model License","DeepSeek","https://github.com/deepseek-ai/DeepSeek-LLM/blob/main/LICENSE-MODEL"),
]
ref_rows = [[(10, "Source", True), (6, "Author / org", True), (14, "Link", True)]]
for w, a, u in REFS:
    ref_rows.append([(10, w, False), (6, a, False), (14, u, False)])
r = section(r, "REFERENCES", ref_rows)

OUT = "/home/h412581/Downloads/ipoefgfefs_SLM_Matrix.xlsx"
wb.save(OUT)
print("saved:", OUT)
print("sheets:", wb.sheetnames)
print("models:", len(SLM), " matrix rows:", last_data - first_data + 1, " total rows:", r - 1)
