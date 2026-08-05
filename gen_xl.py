import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "SLM Selection"

# Colors
HON_RED   = "BF0000"
FULL_G    = "1A7F37"
ALLY_B    = "0550AE"
COMM_O    = "BC4C00"
BLOCK_R   = "CF222E"
HDR_BG    = "1A1A2E"
GRP1      = "0D1B2A"
GRP2      = "16213E"
GRP3      = "0F3460"
GRP4      = "1B1B2F"
GRP5      = "162032"
GRP6      = "0A1628"
GRP7      = "1C1C3A"
GRP8      = "0E1E32"
GRP9      = "192841"
GRP10     = "111827"
GRP11     = "1E2D40"
GRP12     = "0C1A2E"
GRP13     = "182030"
WHITE     = "FFFFFF"
AMBER     = "F5A623"
LTGRAY    = "D0D7DE"
DARKTEXT  = "C8D0DB"

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, color=WHITE, size=9):
    return Font(bold=bold, color=color, size=size, name="Calibri")

def center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def left():
    return Alignment(horizontal="left", vertical="center", wrap_text=True)

thin = Side(style="thin", color="2A3A4A")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

# ── ROW 1: title banner ──────────────────────────────────────────────────────
ws.merge_cells("A1:AK1")
c = ws["A1"]
c.value = "HonDefender SLM Selection Matrix  |  US/EU Compliant Only  |  NDAA §889 Safe  |  Replace: qwen2.5-coder:14b (BLOCKED – Alibaba/China)"
c.fill = fill(HON_RED)
c.font = Font(bold=True, color=WHITE, size=11, name="Calibri")
c.alignment = center()
ws.row_dimensions[1].height = 22

# ── ROW 2: column group headers ──────────────────────────────────────────────
groups = [
    ("A2:A2",  "MODEL",            HDR_BG),
    ("B2:D2",  "COMPLIANCE",       "0D3B66"),
    ("E2:E2",  "PARAMS",           "1A3A2E"),
    ("F2:F2",  "QUANTIZATIONS",    "2A1A3E"),
    ("G2:I2",  "MODEL SIZE",       "3A1A1A"),
    ("J2:L2",  "HARDWARE SUPPORT", "1A2A1A"),
    ("M2:O2",  "RAM USAGE",        "1A1A3A"),
    ("P2:Q2",  "CONTEXT WINDOW",   "2A2A1A"),
    ("R2:U2",  "TOKEN RATE (tok/s)","1A3A3A"),
    ("V2:Y2",  "TASK FIT (primary purpose + ratings)", "2A1A2A"),
    ("Z2:AC2", "FINE-TUNING",      "1A2A3A"),
    ("AD2:AG2","BENCHMARKS",       "3A1A2A"),
    ("AH2:AH2","INFERENCE ENGINES","2A3A1A"),
    ("AI2:AL2","llama.cpp",        "1A1A2A"),
]
for cell_range, label, bg in groups:
    ws.merge_cells(cell_range)
    c = ws[cell_range.split(":")[0]]
    c.value = label
    c.fill = fill(bg)
    c.font = Font(bold=True, color=AMBER, size=9, name="Calibri")
    c.alignment = center()
ws.row_dimensions[2].height = 18

# ── ROW 3: column headers ─────────────────────────────────────────────────────
headers = [
    "Model",
    "License", "Tier", "Countries OK",
    "Params",
    "Quant Types",
    "Size Q4", "Size Q8", "Size F16",
    "NVIDIA (min)", "AMD ROCm", "ARM A53 / Apple",
    "RAM Q4 CPU", "RAM Q8 CPU", "VRAM Q4 GPU",
    "Max Context", "8K Prompt Fit?",
    "CPU x86", "RTX 3090", "A100 80GB", "ARM A53",
    "Primary Design Purpose", "C++ Code Gen", "Analytical Reasoning", "Orchestration / Planning",
    "FT Methods", "FIM (Fill-in-Middle)", "Min FT GPU (QLoRA)", "C++14 Safe",
    "HumanEval", "MultiPL-E C++", "MBPP", "BigCodeBench",
    "Engines",
    "llama.cpp Tag",
    "Other Templates", "Tokenizer",
]
for col, h in enumerate(headers, 1):
    c = ws.cell(row=3, column=col, value=h)
    c.fill = fill("0A1628")
    c.font = Font(bold=True, color=AMBER, size=8, name="Calibri")
    c.alignment = center()
    c.border = border
ws.row_dimensions[3].height = 32

# ── DATA ──────────────────────────────────────────────────────────────────────
ROWS = [
    ["Devstral Small 24B",
     "Apache 2.0", "ALLY", "US, EU, Global",
     "24B",
     "Q4_K_M, Q5_K_M, Q8_0, F16",
     "14 GB", "25 GB", "48 GB",
     "Pascal sm60+ / Turing / Ampere", "RDNA2+ ROCm ✓", "A53: ❌ (14GB too large) | M1+ ✓",
     "~16 GB", "~28 GB", "~16 GB",
     "128K", "✅ YES",
     "3–5", "25–35", "50–70", "❌",
     "Code generation specialist — trained on massive code corpus, best at writing syntactically correct multi-language code. #1 pick for HonDefender custom_logic C++ stitching.", "★★★★★", "★★★", "★★★★",
     "LoRA, QLoRA, Full FT", "❌ No — generates whole functions, not mid-code gaps", "A10G 24 GB (~$1/hr AWS g5.xlarge)", "High — avoids C++17, ARM-safe",
     "~68%", "~62%", "~72%", "~55%",
     "llama.cpp, vLLM, SGLang, TGI, Ollama",
     "mistral",
     "N/A", "SentencePiece"],

    ["Phi-4 14B",
     "MIT", "FULL", "US, Global",
     "14B",
     "Q4_K_M, Q5_K_M, Q8_0, F16",
     "8.4 GB", "15 GB", "28 GB",
     "Volta sm70+ / Ampere / Ada", "RDNA2+ ROCm ✓", "A53: ❌ | M1+ ✓",
     "~10 GB", "~17 GB", "~10 GB",
     "16K", "⚠️ TIGHT",
     "5–8", "40–55", "80–100", "❌",
     "Reasoning & STEM specialist — Microsoft trained it on textbook-quality data for math and logic. Code is secondary strength. Best benchmarks in table but 16K context is risky for HonDefender.", "★★★★", "★★★★★", "★★★★★",
     "LoRA, QLoRA", "❌ No — not a code-completion model", "RTX 3090 24 GB (~$1.21/hr AWS g5.2xlarge)", "High — safe C++14",
     "~80.6%", "~74%", "~81%", "~62%",
     "llama.cpp, vLLM, TGI, Ollama",
     "phi3 / chatml",
     "chatml", "tiktoken (BPE)"],

    ["Codestral 22B",
     "Codestral (verify)", "COMMERCIAL", "Check contract",
     "22B",
     "Q4_K_M, Q5_K_M, Q8_0, F16",
     "13 GB", "23 GB", "44 GB",
     "Volta sm70+ / Ampere / Ada", "RDNA2+ ROCm ✓", "A53: ❌ | M2+ ✓",
     "~15 GB", "~26 GB", "~14 GB",
     "32K", "✅ YES",
     "3–5", "25–35", "50–65", "❌",
     "Code completion & infill specialist — Mistral purpose-built this ONLY for code. Best FIM support. Highest C++ benchmark. BUT license restricts commercial use — verify with Honeywell legal before shipping.", "★★★★★", "★★", "★★★",
     "LoRA (Mistral license approval needed)", "✅ Yes — strongest FIM in table, fills mid-function gaps", "A10G 24 GB (~$1/hr AWS g5.xlarge)", "High — safe C++14",
     "~81.1%", "~76%", "~78%", "~60%",
     "llama.cpp, vLLM, TGI, Ollama",
     "mistral",
     "N/A", "SentencePiece"],

    ["Granite 3.3 Code 8B",
     "Apache 2.0", "FULL", "US, Global",
     "8B",
     "Q4_K_M, Q8_0, F16",
     "4.7 GB", "8.6 GB", "16 GB",
     "Volta sm70+ / Ampere / Ada", "RDNA2+ ROCm ✓", "A53: ❌ | M1+ ✓",
     "~6 GB", "~10 GB", "~5.5 GB",
     "128K", "✅ YES",
     "8–12", "50–70", "100–120", "❌",
     "Enterprise code generation — IBM trained on enterprise codebases. Strict coding patterns, FIM support, Apache 2.0. Best compliance posture (US company). Fits on 12GB GPU for fine-tuning.", "★★★★", "★★★", "★★★",
     "LoRA, QLoRA, Full FT", "✅ Yes — supports FIM for mid-function code completion", "RTX 3060 12 GB (cheapest FT option)", "High — IBM enterprise focus, strict C++14",
     "~60%", "~56%", "~65%", "~48%",
     "llama.cpp, vLLM, TGI, Ollama",
     "llama3",
     "N/A", "BPE"],

    ["Llama 3.1 8B",
     "Llama 3.1 Comm.", "FULL", "US, Global (<700M MAU)",
     "8B",
     "Q4_K_M, Q5_K_M, Q8_0, F16, IQ quants",
     "4.7 GB", "8.6 GB", "16 GB",
     "Volta sm70+ / Ampere / Ada", "RDNA2+ ROCm ✓", "A53: ⚠️ ~1–2 tok/s | M1+ ✓",
     "~6 GB", "~10 GB", "~5.5 GB",
     "128K", "✅ YES",
     "8–12", "50–70", "100–120", "1–2",
     "General-purpose instruction following — balanced across code, reasoning, conversation. Not code-specialized but strong benchmarks. Best ecosystem support (most tutorials, most fine-tuning guides).", "★★★", "★★★", "★★★",
     "LoRA, QLoRA, Full FT", "❌ No — instruction model, not code-completion", "RTX 3060 12 GB (cheapest FT option)", "Medium — mostly safe but verify output",
     "~72.6%", "~62%", "~69%", "~43%",
     "llama.cpp, vLLM, SGLang, TGI, Ollama, TRT-LLM",
     "llama3",
     "N/A", "tiktoken (BPE)"],

    ["Llama 3.3 70B",
     "Llama 3.3 Comm.", "FULL", "US, Global (<700M MAU)",
     "70B",
     "Q4_K_M, Q8_0",
     "42 GB", "75 GB", "140 GB",
     "A100/H100 only (multi-GPU)", "MI250/MI300 only", "A53: ❌ | M2 Ultra only",
     "~48 GB", "~80 GB", "~42 GB (2×A100)",
     "128K", "✅ YES",
     "1–2", "❌ too large", "25–40", "❌",
     "Best-in-class reasoning — Meta's flagship. Highest benchmarks in table. Complex multi-step logic, best C++ accuracy. BUT needs 2×A100 for GPU inference — overkill unless Honeywell has data-center infra.", "★★★★★", "★★★★★", "★★★★★",
     "LoRA only (too large for QLoRA on single GPU)", "❌ No", "4×A100 (~$32/hr AWS p4d) — very expensive", "High — best C++14 compliance in table",
     "~88.4%", "~80%", "~87%", "~68%",
     "llama.cpp (CPU offload), vLLM, SGLang, TGI, TRT-LLM",
     "llama3",
     "N/A", "tiktoken (BPE)"],

    ["Mistral 7B v0.3",
     "Apache 2.0", "ALLY", "US, EU, Global",
     "7B",
     "Q4_K_M, Q5_K_M, Q8_0, F16",
     "4.1 GB", "7.7 GB", "14 GB",
     "Pascal sm60+ / Turing / Ampere", "RDNA2+ ROCm ✓", "A53: ⚠️ ~1–2 tok/s | M1+ ✓",
     "~5.5 GB", "~9.5 GB", "~5 GB",
     "32K", "✅ YES",
     "8–12", "55–75", "110–130", "1–2",
     "General lightweight instruction model — fast, small, widely supported. Weakest code benchmarks in table. Good baseline for POC testing or as a fallback model. Not recommended as primary codegen.", "★★", "★★", "★★",
     "LoRA, QLoRA, Full FT", "❌ No", "RTX 3060 12 GB (cheapest)", "Medium — verify C++14 output",
     "~40.2%", "~38%", "~47%", "~30%",
     "llama.cpp, vLLM, SGLang, TGI, Ollama, ExLlamaV2",
     "mistral",
     "N/A", "SentencePiece"],

    ["CodeLlama 34B",
     "Llama 2 Comm.", "FULL", "US, Global",
     "34B",
     "Q4_K_M, Q5_K_M, Q8_0",
     "20 GB", "36 GB", "68 GB",
     "Volta sm70+ / Ampere", "RDNA2+ ROCm ✓", "A53: ❌ | M2 Pro+ ✓",
     "~24 GB", "~40 GB", "~22 GB",
     "100K", "✅ YES",
     "2–4", "20–30", "40–55", "❌",
     "Dedicated code model with FIM — Meta's code-specialized Llama 2 variant. Strong FIM support (fill-in-middle). Lower benchmark scores vs newer models. Large size (34B) means slow on single GPU.", "★★★★", "★★", "★★",
     "LoRA, QLoRA", "✅ Yes — native FIM, can complete code between prefix and suffix", "2×A100 or 2×RTX 3090 (48 GB total VRAM)", "High — code-specialized, reliable C++14",
     "~48.8%", "~44%", "~55%", "~36%",
     "llama.cpp, vLLM, TGI, Ollama",
     "llama2",
     "N/A", "SentencePiece"],

    ["Phi-3.5-mini 3.8B",
     "MIT", "FULL", "US, Global",
     "3.8B",
     "Q4_K_M, Q5_K_M, Q8_0, F16",
     "2.4 GB", "4.0 GB", "7.6 GB",
     "Volta sm70+ / Ampere / Ada", "RDNA2+ ROCm ✓", "A53: ✅ ~2–4 tok/s | M1+ ✓",
     "~3.5 GB", "~5.5 GB", "~3 GB",
     "128K", "✅ YES",
     "15–25", "80–100", "150+", "2–4",
     "Edge-optimized reasoning — Microsoft's smallest model, designed to run on phones and edge devices. ONLY model that fits on Ambarella S50 camera (2.4 GB Q4). Future path for offline camera-side SLM.", "★★★", "★★★", "★★★",
     "LoRA, QLoRA", "❌ No — too small for reliable FIM", "RTX 3060 12 GB (cheapest)", "Medium — smaller model, verify output",
     "~62.8%", "~55%", "~69%", "~42%",
     "llama.cpp, vLLM, TGI, Ollama, MLC-LLM, ONNX Runtime",
     "phi3",
     "chatml", "BPE"],

    ["Starcoder2 15B",
     "OpenRAIL-M", "ALLY", "US, EU, Global",
     "15B",
     "Q4_K_M, Q8_0, F16",
     "9 GB", "16 GB", "30 GB",
     "Volta sm70+ / Ampere", "RDNA2+ ROCm ✓", "A53: ❌ | M1+ ✓",
     "~11 GB", "~19 GB", "~10.5 GB",
     "16K", "⚠️ TIGHT",
     "4–6", "30–45", "60–80", "❌",
     "Pure code corpus model with FIM — BigCode trained ONLY on source code (no chat, no instruction data). Strong FIM. BUT 16K context is tight for HonDefender 8K prompts, and lower benchmark scores than newer models.", "★★★", "★★", "★★",
     "LoRA, QLoRA", "✅ Yes — strong FIM, trained on code-only corpus", "RTX 3090 24 GB", "Medium — pure code model, check output",
     "~46.4%", "~42%", "~51%", "~38%",
     "llama.cpp, vLLM, TGI, Ollama",
     "custom (verify llama.cpp ≥ b3000)",
     "N/A", "Custom BPE"],

    # ── NEW SMALL EFFICIENT MODELS ──────────────────────────────────────────
    ["Llama 3.2 3B",
     "Llama 3.2 Comm.", "FULL", "US, Global (<700M MAU)",
     "3B",
     "Q4_K_M, Q5_K_M, Q8_0, F16",
     "2.0 GB", "3.5 GB", "6.4 GB",
     "Volta sm70+ / Ampere / Ada", "RDNA2+ ROCm ✓", "A53: ✅ ~4–6 tok/s (fits in 4GB RAM) | M1+ ✓",
     "~2.5 GB", "~4.5 GB", "~2.2 GB",
     "128K", "✅ YES",
     "25–40", "150+", "300+", "4–6",
     "Ultra-lightweight general model — smallest compliant option. Tiny Q4 (2GB). Only model besides Phi-3.5-mini that fits on Ambarella S50. Weak code quality for complex stitching but fast and free.", "★★", "★★", "★★",
     "LoRA, QLoRA, Full FT", "❌ No", "RTX 3060 12 GB (< $0.50/hr)", "Medium — small model, always verify C++",
     "~57.8%", "~48%", "~53%", "~30%",
     "llama.cpp, vLLM, TGI, Ollama, MLC-LLM, ONNX Runtime",
     "llama3",
     "N/A", "tiktoken (BPE)"],

    ["Gemma 3 4B",
     "Gemma ToS", "COMMERCIAL", "Check Honeywell legal — Google ToS",
     "4B",
     "Q4_K_M, Q8_0, BF16",
     "2.5 GB", "4.5 GB", "8.5 GB",
     "Ampere sm80+ preferred / Volta sm70 works", "RDNA2+ ROCm ✓", "A53: ⚠️ ~3–5 tok/s (tight on 4GB) | M1+ ✓",
     "~3.5 GB", "~6 GB", "~3 GB",
     "128K", "✅ YES",
     "20–30", "120+", "250+", "3–5",
     "Efficient reasoning model — Google's smallest Gemma 3. Punches above weight for reasoning and code. Best Qwen-2.5-3B equivalent that is US-origin. Needs legal clearance on Gemma ToS before shipping in Honeywell product.", "★★★", "★★★★", "★★★",
     "LoRA, QLoRA", "❌ No", "RTX 3060 12 GB", "Medium — verify output",
     "~62%", "~54%", "~65%", "~40%",
     "llama.cpp, vLLM, TGI, Ollama",
     "gemma",
     "N/A", "SentencePiece"],

    ["CodeGemma 7B",
     "Gemma ToS", "COMMERCIAL", "Check Honeywell legal — Google ToS",
     "7B",
     "Q4_K_M, Q8_0, BF16",
     "4.5 GB", "8.0 GB", "14 GB",
     "Volta sm70+ / Ampere / Ada", "RDNA2+ ROCm ✓", "A53: ⚠️ ~1–2 tok/s (4.5GB tight) | M1+ ✓",
     "~5.5 GB", "~10 GB", "~5 GB",
     "8K", "🚫 CRITICAL — 8K prompt fills entire window, ZERO room for C++ output",
     "8–12", "55–75", "110+", "1–2",
     "⚠️ CONTEXT DEALBREAKER — Code-specialized Gemma with strong FIM, but 8K context window means your HonDefender prompts (6–8K tokens) leave no room for the C++ output. Cannot use without drastically trimming prompts.", "★★★★", "★★", "★★",
     "LoRA, QLoRA", "✅ Yes — strong FIM support", "RTX 3060 12 GB", "High — code-trained",
     "~44.5%", "~41%", "~52%", "~35%",
     "llama.cpp, vLLM, TGI, Ollama",
     "gemma",
     "N/A", "SentencePiece"],

    # ── BLOCKED REFERENCE ROW (metrics only, cannot use) ──────────────────
    ["⛔ Qwen 2.5 Coder 7B [BLOCKED]",
     "Apache 2.0 (origin blocked)", "BLOCKED", "❌ NDAA §889 — Alibaba/China. Illegal for Honeywell use.",
     "7B",
     "Q4_K_M, Q5_K_M, Q8_0, F16",
     "4.5 GB", "8.0 GB", "14 GB",
     "Volta sm70+ / Ampere / Ada", "RDNA2+ ROCm ✓", "A53: ⚠️ ~1–2 tok/s | M1+ ✓",
     "~5.5 GB", "~10 GB", "~5 GB",
     "128K", "✅ YES",
     "8–12", "55–75", "110–130", "1–2",
     "BLOCKED — China origin (Alibaba). Shown for metric reference ONLY. Best code-per-GB ratio in table. This is what you are replacing. Nearest compliant replacement: Granite 3.3 Code 8B (similar size, Apache 2.0, US origin).", "★★★★★", "★★★", "★★★",
     "LoRA, QLoRA, Full FT", "✅ Yes", "RTX 3060 12 GB", "High",
     "~88.4%", "~76%", "~83%", "~58%",
     "llama.cpp, vLLM, TGI, Ollama",
     "chatml",
     "N/A", "tiktoken"],
]

TIER_COLORS = {"FULL": FULL_G, "ALLY": ALLY_B, "COMMERCIAL": COMM_O, "BLOCKED": BLOCK_R}
FIT_COLORS  = {"✅ YES": "1A4A2A", "⚠️ TIGHT": "4A3A0A", "✅ Yes": "1A4A2A", "❌": "3A0A0A"}
ROW_BG      = ["0D1B2A", "111827"]

for r, row in enumerate(ROWS, 4):
    is_blocked = "BLOCKED" in str(row[2])
    bg = "2A0A0A" if is_blocked else ROW_BG[r % 2]
    for c, val in enumerate(row, 1):
        cell = ws.cell(row=r, column=c, value=val)
        cell.border = border
        cell.alignment = left() if c in (1, 6, 10, 11, 12, 25, 33, 35) else center()
        cell.font = Font(color="FF6B6B" if is_blocked else LTGRAY, size=8, name="Calibri",
                         strike=is_blocked and c not in (3,))
        cell.fill = fill(bg)

        # Model name — amber bold / red for blocked
        if c == 1:
            cell.font = Font(bold=True, color="FF4444" if is_blocked else AMBER,
                             size=9, name="Calibri", strike=is_blocked)
        # Tier badge colors
        if c == 3 and val in TIER_COLORS:
            cell.fill = fill(TIER_COLORS[val] if not is_blocked else BLOCK_R)
            cell.font = Font(bold=True, color=WHITE, size=8, name="Calibri")
        # 8K fit column
        if c == 17:
            fc = FIT_COLORS.get(val, bg)
            if "CRITICAL" in str(val) or "🚫" in str(val):
                fc = "4A0A0A"
            cell.fill = fill(fc)
            cell.font = Font(bold=True, color=WHITE, size=8, name="Calibri")
    ws.row_dimensions[r].height = 50 if is_blocked else 44

# ── COLUMN WIDTHS ─────────────────────────────────────────────────────────────
widths = [22, 18, 12, 22, 7, 32, 8, 8, 8, 28, 20, 26, 10, 10, 16, 8, 12,
          8, 10, 10, 8, 52, 10, 10, 12, 36, 30, 30, 8,
          10, 14, 8, 14, 42, 18, 18, 18]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w

ws.freeze_panes = "B4"

# ── SHEET 2: Inference Engines ─────────────────────────────────────────────────
ws2 = wb.create_sheet("Inference Engines")
ws2.sheet_view.showGridLines = False
eng_headers = ["Engine","ARM A53","Prod Ready","HonDefender Fit","Advantage","Limitation","POC→Prod"]
eng_data = [
    ["llama.cpp","✅ Yes","✅ Yes","★★★★★ USE THIS","No daemon, GGUF, embeddable C++","Single request at a time","Start here — same binary for POC and prod"],
    ["Ollama","❌","⚠️ POC only","★★★ POC","Dead simple setup, pulls GGUF auto","Daemon process, harder to embed","Use for day-1 POC, swap llama.cpp for prod"],
    ["vLLM","❌","✅ Yes","★★★ GPU server","Highest throughput, paged KV cache","CUDA-only, Python, overkill for 1 user","Add when you need concurrent compile requests"],
    ["TGI (HuggingFace)","❌","✅ Yes","★★★","Good REST API, HF native","Heavy Docker, CUDA preferred","Use if you want a managed REST endpoint"],
    ["ExLlamaV2","❌","⚠️","★★ RTX only","Fastest GPTQ on RTX cards","Python, CUDA only","Only if server gets RTX 30xx/40xx GPU"],
    ["TensorRT-LLM","❌","✅ Enterprise","★★ future","Fastest on A100/H100","NVIDIA-only, complex build","Future path if you get A100"],
    ["MLC-LLM","⚠️ some","⚠️","★ edge future","Compiles model to target CPU","Limited model support","Consider if edge SLM ever needed"],
    ["ONNX Runtime","⚠️ Phi only","⚠️","★ Phi only","Wide hardware, Phi-3.5 edge path","Only few models, no GGUF","Phi-3.5-mini ARM path only"],
    ["MLX","❌","Dev only","❌ macOS only","Fast on Apple Silicon","macOS only, not Linux server","Not applicable — server is Ubuntu"],
]
for ci, h in enumerate(eng_headers, 1):
    c = ws2.cell(row=1, column=ci, value=h)
    c.fill = fill("0A1628"); c.font = Font(bold=True, color=AMBER, size=9); c.alignment = center(); c.border = border
for ri, row in enumerate(eng_data, 2):
    for ci, v in enumerate(row, 1):
        c = ws2.cell(row=ri, column=ci, value=v)
        c.fill = fill(ROW_BG[ri%2]); c.font = Font(color=LTGRAY, size=8); c.alignment = left(); c.border = border
eng_widths = [18,10,12,18,36,32,40]
for i,w in enumerate(eng_widths,1): ws2.column_dimensions[get_column_letter(i)].width = w

# ── SHEET 3: References ───────────────────────────────────────────────────────
ws3 = wb.create_sheet("References")
refs = [
    ["#","Paper / Resource","What it covers","URL"],
    [1,"Chen et al. 2021","HumanEval benchmark","arxiv.org/abs/2107.03374"],
    [2,"Cassano et al. 2022","MultiPL-E (C++ benchmark)","arxiv.org/abs/2208.08227"],
    [3,"Austin et al. 2021","MBPP benchmark","arxiv.org/abs/2108.07732"],
    [4,"Zhuo et al. 2024","BigCodeBench","arxiv.org/abs/2406.15877"],
    [5,"Jiang et al. 2023","Mistral 7B paper","arxiv.org/abs/2310.06825"],
    [6,"Microsoft 2024","Phi-4 technical report","arxiv.org/abs/2412.08905"],
    [7,"Microsoft 2024","Phi-3 technical report","arxiv.org/abs/2404.14219"],
    [8,"Meta AI 2024","Llama 3 paper","arxiv.org/abs/2407.21783"],
    [9,"Roziere et al. 2023","CodeLlama paper","arxiv.org/abs/2308.12950"],
    [10,"Lozhkov et al. 2024","Starcoder2 paper","arxiv.org/abs/2402.19173"],
    [11,"Mistral AI 2025","Devstral announcement","mistral.ai/news/devstral"],
    [12,"Mistral AI 2024","Codestral announcement","mistral.ai/news/codestral"],
    [13,"IBM Research 2025","Granite 3.3 Code","research.ibm.com/blog/granite-3-code"],
    [14,"Hu et al. 2021","LoRA paper","arxiv.org/abs/2106.09685"],
    [15,"Dettmers et al. 2023","QLoRA paper","arxiv.org/abs/2305.14314"],
    [16,"Dao et al. 2022","Flash Attention","arxiv.org/abs/2205.14135"],
    [17,"Kwon et al. 2023","vLLM / PagedAttention","arxiv.org/abs/2309.06180"],
    [18,"ggerganov 2023","llama.cpp GitHub","github.com/ggerganov/llama.cpp"],
    [19,"ggerganov 2023","GGUF format spec","github.com/ggerganov/ggml/blob/master/docs/gguf.md"],
    [20,"US Congress 2019","NDAA §889 text","acquisition.gov/FAR/part-4"],
    [21,"BigCode Project","OpenRAIL-M license","bigcode-project.org/docs/pages/bigcode-openrail"],
    [22,"HuggingFace","TGI GitHub","github.com/huggingface/text-generation-inference"],
    [23,"HuggingFace","Open LLM Leaderboard","huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard"],
    [24,"HuggingFace","PEFT / LoRA fine-tuning guide","huggingface.co/docs/peft"],
]
for ri, row in enumerate(refs, 1):
    for ci, v in enumerate(row, 1):
        c = ws3.cell(row=ri, column=ci, value=v)
        if ri == 1:
            c.fill = fill("0A1628"); c.font = Font(bold=True, color=AMBER, size=9)
        else:
            c.fill = fill(ROW_BG[ri%2]); c.font = Font(color=LTGRAY, size=8)
        c.alignment = left(); c.border = border
for i,w in enumerate([5,30,32,50],1): ws3.column_dimensions[get_column_letter(i)].width = w

wb.save("/home/h412581/Downloads/HonDefender_SLM_Matrix.xlsx")
print("Done: /home/h412581/Downloads/HonDefender_SLM_Matrix.xlsx")
