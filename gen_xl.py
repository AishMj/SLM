# ipoefgfefs SLM selection matrix generator
# Sheet 1 "Summary"  - clean, for a non-technical audience
# Sheet 2 "Detailed" - every data column followed by its own Reference column
#
# Sourcing discipline:
#   VERIFIED  = number/fact I can point at a specific published artefact for
#   CALC      = computed here, formula stated inline, nothing measured
#   CHECK     = value is right to the best of my knowledge but the exact table/section
#               citation has NOT been re-read against the source. Must be checked before
#               an architecture review. These are called out, not hidden.

import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HDR   = "BF0000"
GRP   = "1F2937"
REFH  = "4A5568"
SEC   = "0A3069"
FULL_G= "1A7F37"
ALLY_B= "0550AE"
COMM_O= "BC4C00"
OPEN_P= "6F42C1"
WARN  = "F5A623"
BAD   = "CF222E"
ALT   = "F6F8FA"
REFBG = "EFF2F5"

thin = Side(style="thin", color="D0D7DE")
BORD = Border(left=thin, right=thin, top=thin, bottom=thin)

QB = {"Q4_K_M": 0.56, "Q5_K_M": 0.69, "Q8_0": 1.06, "F16": 2.00}
BW_GPU, BW_CPU, EFF_G, EFF_C = 1008.0, 80.0, 0.70, 0.60

def toks(gb, gpu=True):
    bw, eff = (BW_GPU, EFF_G) if gpu else (BW_CPU, EFF_C)
    return round(bw / gb * eff, 1)

def kv_gb(ly, kvh, hd, seq):
    return 2 * ly * kvh * hd * seq * 2 / (1024 ** 3)

# ---- shared source strings ------------------------------------------------
LLCPP = ("github.com/ggml-org/llama.cpp - README 'Supported backends' table and "
         "docs/build.md. CUDA section states compute capability 5.0 (Maxwell) minimum.")

SRC_SIZE = ("CALC. llama.cpp quantization spec, ggml-quants.h and k_quants PR #1684: "
            "Q4_K_M ~4.5 bits/param, Q5_K_M ~5.5, Q8_0 ~8.5, F16 16. "
            "GB = params_B * bits / 8 * 1.024")
SRC_CPURAM = "CALC. file_size * 1.15. The 15% covers llama.cpp context buffers, KV cache and allocator overhead."
SRC_VRAM = ("CALC. weights + KV cache at 8K context. "
            "KV = 2 (K and V) * n_layer * n_kv_head * head_dim * seq_len * 2 bytes (fp16). "
            "Layer/head geometry read from the model config.json on HuggingFace.")
SRC_TOKS_G = ("CALC, NOT MEASURED. Memory-bandwidth bound estimate: RTX 4090 spec bandwidth "
              "1008 GB/s (NVIDIA Ada GPU architecture whitepaper) x 0.70 efficiency / model_size_GB. "
              "No paper or vendor doc publishes tok/s for these models.")
SRC_TOKS_C = ("CALC, NOT MEASURED. DDR5-5600 dual channel = 89.6 GB/s theoretical, used 80 GB/s "
              "x 0.60 efficiency / model_size_GB. No published source exists.")

INF_COMMON = ("INFERENCE (what ipoefgfefs actually runs on) - llama.cpp: NVIDIA CUDA compute capability "
              "5.0+ (Maxwell: GTX 750 Ti, GTX 900 series and newer); AMD ROCm RDNA2+ (RX 6000 series); "
              "Apple Metal (M1 and later); Vulkan; SYCL/oneAPI (Intel); CPU x86-64 AVX2/AVX-512 and "
              "aarch64 NEON.")

def hw(train):
    return "TRAINING: %s  ||  %s" % (train, INF_COMMON)

def hw_src(train_src):
    return ("Training hardware: %s  ||  Inference hardware: %s  ||  "
            "NOTE: papers only ever state the hardware the model was TRAINED on. No paper states what "
            "hardware can RUN the model - that comes entirely from the inference engine documentation." ) % (train_src, LLCPP)

APACHE = "No country restriction. No field-of-use restriction. Patent grant included. Commercial use permitted."
APACHE_SRC = "apache.org/licenses/LICENSE-2.0 - Sections 2 (Copyright Licence) and 3 (Patent Licence). No geographic clause exists in the text."
MIT_OK = "No country restriction. No field-of-use restriction. Commercial use permitted."
MIT_SRC = "opensource.org/license/mit - full text is 2 paragraphs, contains no geographic or use restriction."

LLAMA_OK = ("No country restriction in the licence text. TWO conditions apply: (a) Acceptable Use Policy "
            "prohibits certain applications, (b) if the product exceeds 700M monthly active users a "
            "separate licence must be requested from Meta.")
LLAMA_SRC = ("llama.com/llama3_3/license - Section 2 'Additional Commercial Terms' (700M MAU clause) and "
             "the linked Acceptable Use Policy at llama.com/llama3/use-policy. "
             "VERIFY the MAU threshold against the specific 3.1/3.2 licence version you ship under.")

GEMMA_OK = ("No country restriction stated. Google retains the right to restrict use remotely. "
            "Prohibited Use Policy applies and Google may update it.")
GEMMA_SRC = ("ai.google.dev/gemma/terms - Section 3.2 (Use Restrictions) and the Gemma Prohibited Use "
             "Policy at ai.google.dev/gemma/prohibited_use_policy. NOTE: this is a Terms-of-Use, NOT an "
             "OSI-approved open source licence. Legal review required before shipping.")

# ---- model table ----------------------------------------------------------
# every field carries a matching *_s source string
M = [
 dict(
   n="Qwen2.5-Coder 7B Instruct", n_s="huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct - model card title",
   lic="Apache 2.0", lic_s="huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct/blob/main/LICENSE - full Apache 2.0 text",
   tier="OPEN", ctry=APACHE + " SEPARATE ISSUE: model origin is China (Alibaba Cloud). The licence permits "
        "everything, but US federal procurement rules on component origin are a distinct question - see NDAA 889.",
   ctry_s=APACHE_SRC + "  ||  Origin: Qwen2.5-Coder Technical Report arxiv 2409.12186, author affiliation "
        "'Alibaba Group'.  ||  NDAA 889: acquisition.gov/far/52.204-25.",
   pb=7.6, p="7.6B dense (6.5B non-embedding)",
   p_s="huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct - model card 'Model Details' section states 7.61B "
       "total / 6.53B non-embedding. Cross-check config.json.",
   train="Not disclosed in the technical report",
   train_s="arxiv 2409.12186 - no training-hardware section is present in the paper. CHECK if a later "
           "revision adds one.",
   ly=28, kvh=4, hd=128, ctx="32,768 native (131,072 with YaRN scaling)",
   ctx_s="huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct - config.json max_position_embeddings = 32768; "
         "model card 'Processing Long Texts' section describes YaRN extension to 131072.",
   prim="Code generation - C++ / multi-language",
   prim_s="arxiv 2409.12186 title and abstract: 'Qwen2.5-Coder Technical Report', described as a code-specific model series.",
   sec="Fill-in-the-Middle (FIM) code completion; code reasoning; code repair",
   sec_s="huggingface.co/Qwen/Qwen2.5-Coder-7B - base model card documents the FIM special tokens "
         "<|fim_prefix|>, <|fim_suffix|>, <|fim_middle|>.",
   bench="HumanEval 88.4% | MultiPL-E C++ 63.4% | MBPP 83.5%",
   bench_s="HumanEval: qwenlm.github.io/blog/qwen2.5-coder/ (official Qwen blog, results table).  ||  "
           "MultiPL-E C++ and MBPP: arxiv 2409.12186, multi-language evaluation section.  ||  "
           "CHECK exact table numbers against the PDF before review.",
   eng="llama.cpp, vLLM, SGLang, Ollama, TGI, MLX, TensorRT-LLM",
   eng_s="llama.cpp: GGUF builds published at huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF (official "
         "Qwen repo).  ||  vLLM: docs.vllm.ai supported-models list includes Qwen2ForCausalLM.  ||  "
         "SGLang: docs.sglang.ai supported models.  ||  Ollama: ollama.com/library/qwen2.5-coder.",
   vstat="Benchmarks: CHECK. Licence/params/context: VERIFIED.",
 ),
 dict(
   n="Phi-4 14B", n_s="huggingface.co/microsoft/phi-4 - model card title",
   lic="MIT", lic_s="huggingface.co/microsoft/phi-4/blob/main/LICENSE - MIT text",
   tier="FULL", ctry=MIT_OK + " Origin: United States (Microsoft). No procurement-origin concern.",
   ctry_s=MIT_SRC + "  ||  Origin: arxiv 2412.08905, author affiliation 'Microsoft Research'.",
   pb=14.7, p="14.7B dense",
   p_s="huggingface.co/microsoft/phi-4 - model card 'Model Summary' table, Architecture row states 14B "
       "parameters. config.json for exact geometry.",
   train="1920 x NVIDIA H100-80GB, approx 21 days",
   train_s="arxiv 2412.08905 - training-details section. CHECK: GPU count and duration quoted from memory, "
           "confirm against the PDF.",
   ly=40, kvh=10, hd=128, ctx="16,384",
   ctx_s="huggingface.co/microsoft/phi-4 - model card 'Model Summary' table, Context length row = 16K tokens; "
         "config.json max_position_embeddings = 16384.",
   prim="General reasoning and code generation",
   prim_s="arxiv 2412.08905 abstract - describes a model trained with emphasis on data quality and reasoning, "
          "not a code-specific model.",
   sec="Mathematical reasoning; orchestration / planning (Pass A IR generation)",
   sec_s="arxiv 2412.08905 - reports MATH and GSM8K results alongside general benchmarks.",
   bench="HumanEval 82.6% | MMLU 84.8% | MATH 80.4% | GSM8K 91.5% | MultiPL-E C++ NOT PUBLISHED",
   bench_s="arxiv 2412.08905, main results table comparing against GPT-4o-mini and Qwen2.5-14B.  ||  "
           "CHECK exact table number.  ||  MultiPL-E C++: genuinely absent from the paper - this is a "
           "gap in the published record, not a gap in this research.",
   eng="llama.cpp, vLLM, Ollama, ONNX Runtime, TGI, MLX",
   eng_s="llama.cpp: GGUF at huggingface.co/microsoft/phi-4-gguf (official Microsoft repo).  ||  "
         "ONNX: huggingface.co/microsoft/phi-4-onnx.  ||  vLLM: docs.vllm.ai supported models "
         "(Phi3ForCausalLM architecture).  ||  Ollama: ollama.com/library/phi4.",
   vstat="Benchmarks + training HW: CHECK. Licence/params/context: VERIFIED.",
 ),
 dict(
   n="Granite 3.3 8B Instruct", n_s="huggingface.co/ibm-granite/granite-3.3-8b-instruct - model card title",
   lic="Apache 2.0", lic_s="huggingface.co/ibm-granite/granite-3.3-8b-instruct - model card 'License' field states Apache 2.0",
   tier="FULL", ctry=APACHE + " Origin: United States (IBM). IBM additionally publishes training-data "
        "provenance and offers customer indemnification for Granite models.",
   ctry_s=APACHE_SRC + "  ||  Origin and indemnity: ibm.com/granite - IBM states standard contractual "
          "IP indemnification for Granite. CHECK current terms with IBM before relying on this commercially.",
   pb=8.1, p="8.1B dense",
   p_s="huggingface.co/ibm-granite/granite-3.3-8b-instruct - model card 'Model Architecture' table.",
   train="IBM Blue Vela cluster, NVIDIA H100",
   train_s="Granite model card 'Infrastructure' section names the Blue Vela supercomputing cluster. "
           "CHECK exact GPU count.",
   ly=40, kvh=8, hd=128, ctx="131,072",
   ctx_s="huggingface.co/ibm-granite/granite-3.3-8b-instruct - model card states 128K context; "
         "config.json max_position_embeddings = 131072.",
   prim="General instruction following with code generation and FIM",
   prim_s="Model card 'Intended Use' section lists code-related tasks including code completion.",
   sec="Reasoning; grounded RAG with inline citations; tool/function calling",
   sec_s="Model card documents citation generation and tool-calling capability as first-class features "
         "of the 3.3 release.",
   bench="HumanEval 67.1% | MMLU 65.5% | GSM8K 80.9% | MultiPL-E C++ NOT PUBLISHED",
   bench_s="huggingface.co/ibm-granite/granite-3.3-8b-instruct - model card 'Evaluation Results' table. "
           "IBM publishes no arXiv paper for the 3.3 release, so the model card IS the primary source.  ||  "
           "CHECK values against the current card - IBM revises these tables between point releases.",
   eng="llama.cpp, vLLM, Ollama, TGI, ONNX Runtime",
   eng_s="llama.cpp: GGUF at huggingface.co/ibm-granite/granite-3.3-8b-instruct-GGUF (official IBM repo).  ||  "
         "vLLM: docs.vllm.ai supported models (GraniteForCausalLM).  ||  Ollama: ollama.com/library/granite3.3.",
   vstat="Benchmarks: CHECK against live card. Licence/params/context: VERIFIED.",
 ),
 dict(
   n="Llama 3.1 8B Instruct", n_s="huggingface.co/meta-llama/Llama-3.1-8B-Instruct - model card title",
   lic="Llama 3.1 Community License", lic_s="huggingface.co/meta-llama/Llama-3.1-8B-Instruct/blob/main/LICENSE",
   tier="FULL", ctry=LLAMA_OK + " Origin: United States (Meta).",
   ctry_s=LLAMA_SRC,
   pb=8.0, p="8.03B dense",
   p_s="huggingface.co/meta-llama/Llama-3.1-8B-Instruct - model card 'Model Information' table; "
       "config.json: 32 layers, 8 KV heads (GQA), head_dim 128.",
   train="NVIDIA H100-80GB. Llama 3 family total 39.3M GPU-hours; 8B share 1.46M GPU-hours",
   train_s="arxiv 2407.21783 - training-compute table breaking down GPU-hours per model size. "
           "CHECK the exact figures and table number.",
   ly=32, kvh=8, hd=128, ctx="131,072",
   ctx_s="huggingface.co/meta-llama/Llama-3.1-8B-Instruct - model card states 128K context; "
         "config.json max_position_embeddings = 131072.",
   prim="General instruction following and code generation",
   prim_s="arxiv 2407.21783 - described as a general-purpose foundation model family.",
   sec="Reasoning; tool/function calling; multilingual (8 languages officially supported)",
   sec_s="Model card 'Intended Use' section names tool use and lists the 8 supported languages.",
   bench="HumanEval 72.6% | MMLU 73.0% | GSM8K 84.5% | MultiPL-E C++ NOT PUBLISHED",
   bench_s="arxiv 2407.21783 - instruction-tuned evaluation tables. This is a 90+ page paper; "
           "CHECK the exact table number before citing it in review.",
   eng="llama.cpp, vLLM, SGLang, TensorRT-LLM, Ollama, TGI, MLX, ONNX Runtime, ExecuTorch",
   eng_s="Broadest support of any model here. llama.cpp: GGUF widely published.  ||  "
         "vLLM: docs.vllm.ai (LlamaForCausalLM is the reference architecture).  ||  "
         "TensorRT-LLM: github.com/NVIDIA/TensorRT-LLM support matrix lists Llama explicitly.  ||  "
         "ExecuTorch: pytorch.org/executorch llama example.",
   vstat="Benchmarks + training HW: CHECK. Licence/params/context: VERIFIED.",
 ),
 dict(
   n="DeepSeek-Coder-V2-Lite Instruct", n_s="huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
   lic="DeepSeek License Agreement", lic_s="github.com/deepseek-ai/DeepSeek-LLM/blob/main/LICENSE-MODEL - "
       "custom licence, permits commercial use but carries use restrictions in an attached policy.",
   tier="OPEN", ctry="No country restriction in the licence, but it is NOT Apache/MIT - it carries "
        "an attached use-restriction policy. Origin: China (DeepSeek). Same procurement-origin question "
        "as Qwen. LEGAL REVIEW REQUIRED - this is the least permissive licence in the shortlist.",
   ctry_s="github.com/deepseek-ai/DeepSeek-LLM/blob/main/LICENSE-MODEL - see the 'Use Restrictions' "
          "attachment.  ||  Origin: arxiv 2406.11931, author affiliation 'DeepSeek-AI'.",
   pb=15.7, p="15.7B total MoE / 2.4B active per token",
   p_s="arxiv 2406.11931 - architecture section states 16B total with 2.4B activated. "
       "config.json for expert count and routing.",
   train="Not clearly disclosed for the Lite variant",
   train_s="arxiv 2406.11931 - training-infrastructure detail is given for the full V2, not clearly "
           "separated for Lite. CHECK.",
   ly=27, kvh=16, hd=128, ctx="131,072",
   ctx_s="huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct - config.json "
         "max_position_embeddings = 163840; model card states 128K usable. CHECK which figure applies.",
   prim="Code generation - C++ / multi-language (MoE)",
   prim_s="arxiv 2406.11931 title: 'DeepSeek-Coder-V2: Breaking the Barrier of Closed-Source Models in Code Intelligence'.",
   sec="Fill-in-the-Middle; mathematical reasoning",
   sec_s="Model card documents FIM tokens; paper reports math benchmarks alongside code.",
   bench="HumanEval 81.1% | MultiPL-E C++ 56.5% | MBPP+ 68.8%",
   bench_s="arxiv 2406.11931 - code-benchmark tables. CHECK exact table numbers.",
   eng="llama.cpp, vLLM, SGLang",
   eng_s="llama.cpp: GGUF community builds (no official DeepSeek GGUF repo - CHECK provenance of any "
         "GGUF you download).  ||  vLLM: docs.vllm.ai supported models (DeepseekV2ForCausalLM).  ||  "
         "SGLang: docs.sglang.ai.  ||  NOTE: MoE support in llama.cpp is newer and less battle-tested "
         "than dense-model support.",
   vstat="Benchmarks + context: CHECK. Licence: VERIFIED but restrictive.",
 ),
 dict(
   n="StarCoder2 15B", n_s="huggingface.co/bigcode/starcoder2-15b - model card title",
   lic="BigCode OpenRAIL-M v1", lic_s="huggingface.co/spaces/bigcode/bigcode-model-license-agreement - "
       "behavioural-use licence, royalty-free but with mandatory use restrictions that flow down to "
       "derivatives.",
   tier="ALLY", ctry="No country restriction. HAS behavioural use restrictions that you must pass on to "
        "anyone you distribute derivatives to. Origin: EU + US (ServiceNow, Hugging Face, NVIDIA).",
   ctry_s="BigCode OpenRAIL-M v1 Attachment A lists prohibited uses; Section 'Distribution and "
          "Redistribution' requires the restrictions to flow down.  ||  Origin: arxiv 2402.19173 author list.",
   pb=16.0, p="16.0B dense (marketed as 15B)",
   p_s="huggingface.co/bigcode/starcoder2-15b - config.json. NOTE the marketing name understates the "
       "actual parameter count; this sits at the top of the SLM range.",
   train="1024 x NVIDIA A100-80GB",
   train_s="arxiv 2402.19173 - training-infrastructure section. CHECK exact GPU count.",
   ly=40, kvh=4, hd=128, ctx="16,384",
   ctx_s="huggingface.co/bigcode/starcoder2-15b - config.json max_position_embeddings = 16384; "
         "sliding-window attention of 4096 also configured. CHECK the interaction between the two.",
   prim="Code generation and Fill-in-the-Middle (base model, NOT instruction tuned)",
   prim_s="arxiv 2402.19173 - StarCoder2 is released as a base model. The card explicitly notes it is "
          "not an instruction-following model.",
   sec="Code completion across 600+ programming languages; repository-level context",
   sec_s="arxiv 2402.19173 - The Stack v2 covers 600+ languages; paper describes repo-level training context.",
   bench="HumanEval 46.4% | MultiPL-E C++ 41.4%",
   bench_s="arxiv 2402.19173 - evaluation tables. MultiPL-E is reported per-language in this paper, "
           "which is unusual and useful. CHECK exact table numbers.",
   eng="llama.cpp, vLLM, TGI, Ollama",
   eng_s="llama.cpp: GGUF community builds.  ||  vLLM: docs.vllm.ai (Starcoder2ForCausalLM).  ||  "
         "TGI: natively supported, BigCode and HF are the same ecosystem.",
   vstat="Benchmarks: CHECK. Licence: VERIFIED - note the flow-down obligation.",
 ),
 dict(
   n="CodeGemma 7B IT", n_s="huggingface.co/google/codegemma-7b-it - model card title",
   lic="Gemma Terms of Use", lic_s="ai.google.dev/gemma/terms - NOT an OSI open source licence",
   tier="COMMERCIAL", ctry=GEMMA_OK + " Origin: United States (Google).",
   ctry_s=GEMMA_SRC,
   pb=8.5, p="8.5B dense (marketed as 7B)",
   p_s="huggingface.co/google/codegemma-7b-it - config.json. Large vocabulary (256k tokens) inflates "
       "the parameter count above the marketing name.",
   train="Google TPUv5e",
   train_s="CodeGemma report on ai.google.dev/gemma/docs/codegemma - hardware section. CHECK.",
   ly=28, kvh=16, hd=256, ctx="8,192",
   ctx_s="huggingface.co/google/codegemma-7b-it - config.json max_position_embeddings = 8192. "
         "THIS IS THE ELIMINATING CONSTRAINT for ipoefgfefs: a 6-8K prompt fills the entire window.",
   prim="Code generation and Fill-in-the-Middle",
   prim_s="ai.google.dev/gemma/docs/codegemma/model_card - 'Model Information' describes code completion "
          "and generation as the intended use.",
   sec="Code chat; natural-language-to-code",
   sec_s="Same model card, 'Intended Usage' section distinguishes the -it variant as chat-tuned.",
   bench="HumanEval 56.1% | MultiPL-E C++ NOT PUBLISHED",
   bench_s="ai.google.dev/gemma/docs/codegemma/model_card - evaluation table. Google publishes the "
           "CodeGemma report as documentation rather than a peer-reviewed paper. CHECK current values.",
   eng="llama.cpp, Ollama, vLLM",
   eng_s="llama.cpp: GGUF at huggingface.co/google/codegemma-7b-it-GGUF (official Google repo).  ||  "
         "Ollama: ollama.com/library/codegemma.  ||  vLLM: docs.vllm.ai (GemmaForCausalLM).",
   vstat="Benchmarks: CHECK. Context 8K: VERIFIED - this is the disqualifier.",
 ),
 dict(
   n="Phi-3.5-mini 3.8B Instruct", n_s="huggingface.co/microsoft/Phi-3.5-mini-instruct - model card title",
   lic="MIT", lic_s="huggingface.co/microsoft/Phi-3.5-mini-instruct/blob/main/LICENSE - MIT text",
   tier="FULL", ctry=MIT_OK + " Origin: United States (Microsoft).",
   ctry_s=MIT_SRC + "  ||  Origin: arxiv 2404.14219 author affiliation 'Microsoft'.",
   pb=3.8, p="3.8B dense",
   p_s="huggingface.co/microsoft/Phi-3.5-mini-instruct - model card 'Model Summary'; "
       "config.json: 32 layers, 32 heads, NO grouped-query attention.",
   train="512 x NVIDIA H100-80GB, 10 days (Phi-3-mini figure)",
   train_s="arxiv 2404.14219 - training section. NOTE this figure is for Phi-3-mini; the 3.5 refresh "
           "may differ. CHECK.",
   ly=32, kvh=32, hd=96, ctx="131,072",
   ctx_s="huggingface.co/microsoft/Phi-3.5-mini-instruct - config.json max_position_embeddings = 131072 "
         "with LongRoPE scaling. WARNING: no GQA means the KV cache is unusually large at long context - "
         "see the VRAM @Full ctx column.",
   prim="General instruction following, reasoning-dense for its size",
   prim_s="arxiv 2404.14219 abstract - positions the model as matching much larger models on reasoning.",
   sec="Code generation; mathematical reasoning; long-context retrieval",
   sec_s="Model card evaluation tables cover code, math and long-context (RULER, RepoQA) benchmarks.",
   bench="HumanEval 62.8% | MMLU 69.0% | GSM8K 86.2%",
   bench_s="huggingface.co/microsoft/Phi-3.5-mini-instruct - model card evaluation tables. The 3.5 "
           "refresh is documented on the card rather than in a separate paper. CHECK current values.",
   eng="llama.cpp, ONNX Runtime, Ollama, vLLM, MLX",
   eng_s="ONNX: huggingface.co/microsoft/Phi-3.5-mini-instruct-onnx (official Microsoft repo, includes "
         "INT4 builds for CPU and DirectML).  ||  llama.cpp: GGUF community builds.  ||  "
         "Ollama: ollama.com/library/phi3.5.",
   vstat="Benchmarks + training HW: CHECK. Licence/params/context: VERIFIED.",
 ),
 dict(
   n="Llama 3.2 3B Instruct", n_s="huggingface.co/meta-llama/Llama-3.2-3B-Instruct - model card title",
   lic="Llama 3.2 Community License", lic_s="huggingface.co/meta-llama/Llama-3.2-3B-Instruct/blob/main/LICENSE",
   tier="FULL", ctry=LLAMA_OK + " ADDITIONAL RESTRICTION: the Llama 3.2 licence excludes use by "
        "individuals or companies domiciled in the EU for the multimodal models. VERIFY whether this "
        "clause affects the text-only 3B before shipping in Europe. Origin: United States (Meta).",
   ctry_s=LLAMA_SRC + "  ||  EU restriction: Llama 3.2 licence Acceptable Use / territory clause. "
          "THIS IS A REAL AND UNUSUAL CLAUSE - have legal read it directly, do not rely on this summary.",
   pb=3.2, p="3.21B dense",
   p_s="huggingface.co/meta-llama/Llama-3.2-3B-Instruct - model card 'Model Information'; config.json: "
       "28 layers, 8 KV heads (GQA), head_dim 128. Distilled from Llama 3.1 8B and 70B.",
   train="NVIDIA H100-80GB. 3B share: 460K GPU-hours",
   train_s="Llama 3.2 model card 'Training Energy Use' table gives GPU-hours per size. CHECK exact figure.",
   ly=28, kvh=8, hd=128, ctx="131,072",
   ctx_s="huggingface.co/meta-llama/Llama-3.2-3B-Instruct - config.json max_position_embeddings = 131072.",
   prim="General instruction following, on-device / edge deployment",
   prim_s="ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices/ - the 1B and 3B are explicitly "
          "positioned for edge and mobile.",
   sec="Code generation; summarization; tool calling; the only text SLM here viable on Cortex-A53",
   sec_s="Meta blog names summarization, instruction following and rewriting as the target on-device tasks. "
         "Edge viability at Q4 is a CALC from the 1.9 GB file size against the S50 memory budget.",
   bench="HumanEval 57.8% | MMLU 63.4% | GSM8K 77.7%",
   bench_s="ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices/ and the HuggingFace model card "
           "evaluation table. No arXiv paper for 3.2. CHECK current values.",
   eng="llama.cpp (aarch64 NEON), ONNX Runtime, MLC-LLM, Ollama, ExecuTorch",
   eng_s="ExecuTorch: pytorch.org/executorch - Meta's own on-device runtime, Llama 3.2 is the reference "
         "example.  ||  llama.cpp: aarch64 NEON path documented in docs/build.md.  ||  "
         "MLC-LLM: llm.mlc.ai model library.",
   vstat="EU licence clause: MUST BE VERIFIED BY LEGAL. Benchmarks: CHECK.",
 ),
 dict(
   n="Mistral 7B Instruct v0.3", n_s="huggingface.co/mistralai/Mistral-7B-Instruct-v0.3 - model card title",
   lic="Apache 2.0", lic_s="huggingface.co/mistralai/Mistral-7B-Instruct-v0.3 - model card licence field",
   tier="ALLY", ctry=APACHE + " Origin: France (Mistral AI) - EU, allied jurisdiction.",
   ctry_s=APACHE_SRC + "  ||  Origin: arxiv 2310.06825 author affiliation 'Mistral AI'.",
   pb=7.2, p="7.25B dense",
   p_s="huggingface.co/mistralai/Mistral-7B-Instruct-v0.3 - config.json: 32 layers, 8 KV heads (GQA).",
   train="Not disclosed",
   train_s="arxiv 2310.06825 - the paper contains no training-hardware disclosure. This is a genuine "
           "absence, not a gap in this research.",
   ly=32, kvh=8, hd=128, ctx="32,768",
   ctx_s="huggingface.co/mistralai/Mistral-7B-Instruct-v0.3 - config.json max_position_embeddings = 32768. "
         "NOTE v0.3 extended this from v0.2.",
   prim="General instruction following",
   prim_s="arxiv 2310.06825 - general-purpose model, NOT code specialised.",
   sec="Function calling (added in v0.3); multilingual",
   sec_s="Model card release notes for v0.3 list extended vocabulary and function-calling support.",
   bench="MMLU 62.5% | HumanEval 36.5% (leaderboard only, NOT in the paper)",
   bench_s="MMLU: arxiv 2310.06825 results table.  ||  HumanEval: THE PAPER DOES NOT REPORT IT. "
           "Value taken from evalplus.github.io/leaderboard.html - a third-party leaderboard, weaker "
           "evidence than a paper. Flag this explicitly in review.",
   eng="llama.cpp, vLLM, SGLang, Ollama, TGI, MLX, ONNX Runtime",
   eng_s="vLLM: docs.vllm.ai (MistralForCausalLM).  ||  llama.cpp: GGUF widely published.  ||  "
         "Ollama: ollama.com/library/mistral.",
   vstat="HumanEval is leaderboard-sourced, NOT from the paper. Everything else: VERIFIED/CHECK.",
 ),
 dict(
   n="DeepSeek-R1-Distill-Qwen-14B", n_s="huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
   lic="MIT", lic_s="huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B - model card licence field "
       "states MIT. NOTE: the distilled models are MIT even though base DeepSeek models use a custom licence.",
   tier="OPEN", ctry=MIT_OK + " CAVEAT: the model is distilled from DeepSeek-R1 onto a Qwen2.5-14B base. "
        "The Qwen base carries Apache 2.0. Both are permissive but the lineage crosses two licences - "
        "have legal confirm the stack. Origin: China (DeepSeek + Alibaba base).",
   ctry_s=MIT_SRC + "  ||  Lineage: arxiv 2501.12948 - the distillation section names the Qwen2.5 base "
          "models used.  ||  CONFIRM the combined licence position with legal.",
   pb=14.8, p="14.8B dense (Qwen2.5-14B architecture)",
   p_s="huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B - config.json matches Qwen2.5-14B geometry.",
   train="Distillation only - no large-scale pretraining hardware disclosed",
   train_s="arxiv 2501.12948 - distillation is described as SFT on R1-generated reasoning traces. "
           "Hardware for the distillation run is not stated.",
   ly=48, kvh=8, hd=128, ctx="131,072",
   ctx_s="config.json max_position_embeddings = 131072 (inherited from the Qwen2.5-14B base).",
   prim="Chain-of-thought reasoning",
   prim_s="arxiv 2501.12948 - the R1 series is explicitly a reasoning model family.",
   sec="Mathematical problem solving; planning / orchestration (Pass A)",
   sec_s="Paper reports MATH-500 and AIME as the headline benchmarks.",
   bench="MATH-500 93.9% | AIME 2024 69.7% | HumanEval NOT PUBLISHED | MMLU NOT PUBLISHED",
   bench_s="arxiv 2501.12948 - distilled-model comparison table. CHECK exact table number.  ||  "
           "NOTE: no code benchmark is published for this distill, so its C++ ability is UNKNOWN. "
           "Do not assume it inherits Qwen2.5-Coder ability - the base is Qwen2.5 general, not Coder.",
   eng="llama.cpp, vLLM, SGLang, Ollama",
   eng_s="llama.cpp: GGUF community builds.  ||  vLLM: docs.vllm.ai (Qwen2ForCausalLM architecture).  ||  "
         "Ollama: ollama.com/library/deepseek-r1.",
   vstat="Code ability UNKNOWN - no code benchmark published. Benchmarks: CHECK.",
 ),
 dict(
   n="Gemma 3 4B IT", n_s="huggingface.co/google/gemma-3-4b-it - model card title",
   lic="Gemma Terms of Use", lic_s="ai.google.dev/gemma/terms - NOT an OSI open source licence",
   tier="COMMERCIAL", ctry=GEMMA_OK + " Origin: United States (Google).",
   ctry_s=GEMMA_SRC,
   pb=4.3, p="4.3B dense (multimodal: text + vision)",
   p_s="huggingface.co/google/gemma-3-4b-it - model card; config.json includes a SigLIP vision tower.",
   train="Google TPUv5p",
   train_s="arxiv 2503.19786 - training-infrastructure section. CHECK.",
   ly=34, kvh=4, hd=256, ctx="131,072",
   ctx_s="huggingface.co/google/gemma-3-4b-it - model card states 128K for the 4B and above; "
         "config.json max_position_embeddings = 131072.",
   prim="General instruction following with vision (image to text)",
   prim_s="arxiv 2503.19786 - Gemma 3 introduces multimodality to the Gemma family at 4B and above.",
   sec="Multilingual (140+ languages claimed); basic code generation",
   sec_s="Model card 'Model Information' section states the language coverage.",
   bench="HumanEval 36.0% | MMLU 59.6%",
   bench_s="arxiv 2503.19786 - evaluation tables. CHECK exact table number.  ||  "
           "NOTE the low HumanEval: multimodal capability at 4B comes at a real cost to code ability.",
   eng="llama.cpp, Ollama, vLLM, MLX",
   eng_s="llama.cpp: GGUF at huggingface.co/google/gemma-3-4b-it-qat-q4_0-gguf (official Google "
         "quantization-aware-trained build - better quality than post-hoc Q4).  ||  "
         "Ollama: ollama.com/library/gemma3.",
   vstat="Benchmarks: CHECK. Licence: VERIFIED - Terms of Use, not open source.",
 ),
 dict(
   n="Qwen2-VL 7B Instruct", n_s="huggingface.co/Qwen/Qwen2-VL-7B-Instruct - model card title",
   lic="Apache 2.0", lic_s="huggingface.co/Qwen/Qwen2-VL-7B-Instruct - model card licence field",
   tier="OPEN", ctry=APACHE + " Origin: China (Alibaba Cloud). Same procurement-origin question as "
        "Qwen2.5-Coder.",
   ctry_s=APACHE_SRC + "  ||  Origin: arxiv 2409.12191 author affiliation 'Alibaba Group'.",
   pb=8.3, p="8.3B dense (7.6B LLM + 675M vision encoder)",
   p_s="huggingface.co/Qwen/Qwen2-VL-7B-Instruct - config.json shows the vision tower and LLM separately.",
   train="Not disclosed",
   train_s="arxiv 2409.12191 - no training-hardware disclosure located. CHECK.",
   ly=28, kvh=4, hd=128, ctx="32,768",
   ctx_s="config.json max_position_embeddings = 32768. Naive Dynamic Resolution means image token count "
         "varies with input resolution - a large image can consume a lot of the window. IMPORTANT for sizing.",
   prim="Image to text - visual question answering and document understanding",
   prim_s="arxiv 2409.12191 title: 'Qwen2-VL: Enhancing Vision-Language Model's Perception of the World "
          "at Any Resolution'.",
   sec="OCR / text-in-image reading; video understanding (accepts frame sequences); multilingual OCR",
   sec_s="Paper documents video input support and multilingual text recognition. DocVQA 94.5% is the "
         "strongest OCR-adjacent number in this sheet.",
   bench="MMMU 54.1% | DocVQA 94.5% | MathVista 58.2%",
   bench_s="arxiv 2409.12191 - main results tables. CHECK exact table numbers.",
   eng="vLLM, SGLang, llama.cpp, transformers",
   eng_s="vLLM: docs.vllm.ai multimodal-models list (Qwen2VLForConditionalGeneration).  ||  "
         "llama.cpp: vision support added but CHECK current status - the multimodal path in llama.cpp "
         "lags the text path significantly.",
   vstat="Benchmarks: CHECK. llama.cpp vision support: VERIFY CURRENT STATE.",
 ),
 dict(
   n="Phi-3.5-Vision 4.2B", n_s="huggingface.co/microsoft/Phi-3.5-vision-instruct - model card title",
   lic="MIT", lic_s="huggingface.co/microsoft/Phi-3.5-vision-instruct/blob/main/LICENSE - MIT text",
   tier="FULL", ctry=MIT_OK + " Origin: United States (Microsoft). The most permissive VLM here.",
   ctry_s=MIT_SRC,
   pb=4.2, p="4.2B dense (Phi-3.5-mini LLM + CLIP ViT-L/14 vision encoder)",
   p_s="huggingface.co/microsoft/Phi-3.5-vision-instruct - model card 'Model Architecture' states the "
       "image encoder is CLIP ViT-L/14-336.",
   train="256 x NVIDIA A100-80GB, 6 days",
   train_s="Model card 'Training' section. CHECK exact figures.",
   ly=32, kvh=32, hd=96, ctx="131,072",
   ctx_s="config.json max_position_embeddings = 131072. Supports multi-frame / multi-image input, "
         "which is relevant for comparing camera frames.",
   prim="Image to text - captioning, OCR, chart and table reasoning",
   prim_s="Model card 'Intended Uses' - names general image understanding, OCR and chart comprehension.",
   sec="Multi-frame / video-frame comparison; document understanding",
   sec_s="Model card explicitly documents multi-image and video-frame summarization as a supported use.",
   bench="MMBench 81.9% | MMMU 43.0% | TextVQA 72.0%",
   bench_s="huggingface.co/microsoft/Phi-3.5-vision-instruct - model card evaluation tables. "
           "The 3.5-vision refresh is documented on the card. CHECK current values.",
   eng="llama.cpp, ONNX Runtime, vLLM, transformers",
   eng_s="ONNX: huggingface.co/microsoft/Phi-3.5-vision-instruct-onnx (official).  ||  "
         "vLLM: docs.vllm.ai multimodal list.  ||  llama.cpp: CHECK current vision support state.",
   vstat="Benchmarks + training HW: CHECK. Licence: VERIFIED - MIT, cleanest VLM licence here.",
 ),
 dict(
   n="Llama 3.2 11B Vision Instruct", n_s="huggingface.co/meta-llama/Llama-3.2-11B-Vision-Instruct",
   lic="Llama 3.2 Community License", lic_s="huggingface.co/meta-llama/Llama-3.2-11B-Vision-Instruct/blob/main/LICENSE",
   tier="FULL", ctry=LLAMA_OK + " CRITICAL: the Llama 3.2 licence explicitly EXCLUDES use of the "
        "MULTIMODAL models by individuals or companies domiciled in the EU. This model is multimodal. "
        "If ipoefgfefs ships in Europe this is a hard blocker. Origin: United States (Meta).",
   ctry_s=LLAMA_SRC + "  ||  EU multimodal exclusion: stated in the Llama 3.2 licence / Acceptable Use "
          "Policy. THIS IS THE SINGLE MOST IMPORTANT LEGAL LINE IN THIS SHEET - have counsel read the "
          "licence text directly.",
   pb=10.6, p="10.6B dense (8B text base + vision adapter)",
   p_s="huggingface.co/meta-llama/Llama-3.2-11B-Vision-Instruct - model card; the vision adapter uses "
       "cross-attention layers into a frozen Llama 3.1 8B text model.",
   train="NVIDIA H100-80GB",
   train_s="Llama 3.2 model card 'Training Energy Use' table. CHECK GPU-hours for the 11B specifically.",
   ly=40, kvh=8, hd=128, ctx="131,072",
   ctx_s="config.json max_position_embeddings = 131072. NOTE the cross-attention design means image "
         "tokens do not consume the text context the way they do in Qwen2-VL.",
   prim="Image to text - visual reasoning, captioning, document QA",
   prim_s="ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices/ - names image reasoning, "
          "captioning and chart/graph understanding.",
   sec="Chart and diagram understanding; document VQA",
   sec_s="Meta blog and model card list DocVQA and ChartQA as headline capabilities.",
   bench="MMMU 50.7% | DocVQA 88.4% | ChartQA 83.4%",
   bench_s="ai.meta.com/blog/llama-3-2-connect-2024-edge-mobile-devices/ and the model card evaluation "
           "table. No arXiv paper for 3.2. CHECK current values.",
   eng="vLLM, TGI, transformers, llama.cpp (vision path partial)",
   eng_s="vLLM: docs.vllm.ai multimodal list (MllamaForConditionalGeneration).  ||  "
         "llama.cpp: cross-attention vision architecture is NOT fully supported - VERIFY before "
         "assuming a GGUF path exists.",
   vstat="EU MULTIMODAL EXCLUSION - MUST BE VERIFIED BY LEGAL BEFORE ANY EU DEPLOYMENT.",
 ),
 dict(
   n="InternVL2 8B", n_s="huggingface.co/OpenGVLab/InternVL2-8B - model card title",
   lic="MIT", lic_s="huggingface.co/OpenGVLab/InternVL2-8B - model card licence field states MIT. "
       "CHECK: the 8B uses an InternLM2.5 base whose own licence terms should be confirmed.",
   tier="OPEN", ctry=MIT_OK + " CAVEAT: verify the base-model licence in the lineage. "
        "Origin: China (Shanghai AI Laboratory / OpenGVLab).",
   ctry_s=MIT_SRC + "  ||  Base model lineage: model card 'Model Details' names InternLM2.5-7B-chat as "
          "the language component. CONFIRM its licence separately.",
   pb=8.1, p="8.1B dense (InternViT-300M vision + InternLM2.5-7B language)",
   p_s="huggingface.co/OpenGVLab/InternVL2-8B - model card 'Model Details' component table.",
   train="Not clearly disclosed",
   train_s="No dedicated arXiv paper for InternVL2 specifically; InternVL 1.0/1.5 papers exist "
           "(arxiv 2312.14238, 2404.16821). CHECK which paper actually covers the 2.0 release.",
   ly=32, kvh=8, hd=128, ctx="8,192",
   ctx_s="config.json max_position_embeddings = 8192. LIMITING for ipoefgfefs at a 6-8K prompt.",
   prim="Image to text - multimodal understanding",
   prim_s="huggingface.co/OpenGVLab/InternVL2-8B model card 'Introduction'.",
   sec="Document OCR; chart understanding; multi-image comparison",
   sec_s="Model card evaluation tables cover DocVQA, ChartQA and multi-image benchmarks.",
   bench="MMBench 81.7% | MMMU 51.2% | DocVQA 91.6%",
   bench_s="huggingface.co/OpenGVLab/InternVL2-8B model card evaluation tables and the OpenCompass "
           "multimodal leaderboard at rank.opencompass.org.cn/leaderboard-multimodal. "
           "LEADERBOARD-SOURCED in part - weaker evidence than a paper. CHECK.",
   eng="LMDeploy, vLLM, transformers",
   eng_s="LMDeploy: github.com/InternLM/lmdeploy - the first-party runtime from the same lab.  ||  "
         "vLLM: docs.vllm.ai multimodal list (InternVLChatModel).  ||  "
         "NO official GGUF - llama.cpp path is unproven for this model.",
   vstat="Benchmarks partly leaderboard-sourced. Base-model licence lineage: VERIFY.",
 ),
 dict(
   n="LLaVA-1.6 (NeXT) 13B", n_s="huggingface.co/llava-hf/llava-v1.6-vicuna-13b-hf - model card",
   lic="Apache 2.0 (code) - CHECK base weights", lic_s="github.com/haotian-liu/LLaVA - repo licence is "
       "Apache 2.0, BUT the Vicuna-13B language base derives from Llama 2 and carries the Llama 2 "
       "Community Licence. THE EFFECTIVE LICENCE IS THE MORE RESTRICTIVE OF THE TWO.",
   tier="FULL", ctry="Licence stack is layered: LLaVA code Apache 2.0 over Vicuna over Llama 2. "
        "Llama 2 Community Licence terms therefore apply, including its Acceptable Use Policy. "
        "LEGAL REVIEW REQUIRED - this is the messiest licence position in the sheet. Origin: US.",
   ctry_s="LLaVA repo licence: github.com/haotian-liu/LLaVA/blob/main/LICENSE.  ||  "
          "Vicuna lineage: lmsys.org/blog/2023-03-30-vicuna.  ||  "
          "Llama 2 licence: ai.meta.com/llama/license.  ||  Have counsel trace the full chain.",
   pb=13.4, p="13.4B dense (Vicuna-13B + CLIP ViT-L/14-336)",
   p_s="huggingface.co/llava-hf/llava-v1.6-vicuna-13b-hf - config.json.",
   train="8 x NVIDIA A100-80GB (LLaVA-1.5 figure)",
   train_s="arxiv 2310.03744 - training section states roughly 1 day on 8xA100 for the 13B. "
           "CHECK whether 1.6 differs.",
   ly=40, kvh=40, hd=128, ctx="4,096",
   ctx_s="config.json max_position_embeddings = 4096 (Vicuna/Llama 2 inheritance). "
         "SEVERELY LIMITING - a 6-8K ipoefgfefs prompt does not fit at all.",
   prim="Image to text - visual instruction following",
   prim_s="arxiv 2310.03744 title: 'Improved Baselines with Visual Instruction Tuning'.",
   sec="Visual question answering; OCR (weaker than Qwen2-VL)",
   sec_s="Paper evaluation covers VQA benchmarks; TextVQA 67.1% is materially below Qwen2-VL.",
   bench="MMBench 70.0% | TextVQA 67.1% | MMMU 35.9%",
   bench_s="arxiv 2310.03744 evaluation tables for 1.5; 1.6/NeXT results are published on the "
           "llava-vl.github.io blog rather than in a paper. CHECK which release each number belongs to - "
           "1.5 and 1.6 numbers are frequently conflated in secondary sources.",
   eng="llama.cpp, vLLM, SGLang, transformers",
   eng_s="llama.cpp: LLaVA has the most mature vision support in llama.cpp of any model here "
         "(clip.cpp / llava.cpp).  ||  vLLM: docs.vllm.ai multimodal list.  ||  "
         "SGLang: docs.sglang.ai - LLaVA is a documented example.",
   vstat="LICENCE CHAIN MUST BE TRACED BY LEGAL. Context 4K disqualifies it regardless.",
 ),
 dict(
   n="PaliGemma 3B mix-448", n_s="huggingface.co/google/paligemma-3b-mix-448 - model card title",
   lic="Gemma Terms of Use", lic_s="ai.google.dev/gemma/terms",
   tier="COMMERCIAL", ctry=GEMMA_OK + " Origin: United States (Google).",
   ctry_s=GEMMA_SRC,
   pb=2.9, p="2.9B dense (SigLIP-So400m vision + Gemma-2B language)",
   p_s="arxiv 2407.07726 - architecture section names both components; config.json confirms.",
   train="Google TPUv5e",
   train_s="arxiv 2407.07726 - training-infrastructure section. CHECK.",
   ly=18, kvh=1, hd=256, ctx="8,192",
   ctx_s="config.json max_position_embeddings = 8192. NOTE: multi-query attention (1 KV head) makes the "
         "KV cache exceptionally small - see the VRAM columns.",
   prim="Image to text - captioning and visual QA",
   prim_s="arxiv 2407.07726 - positioned as a versatile base model INTENDED TO BE FINE-TUNED, "
          "not used zero-shot.",
   sec="OCR; referring-expression segmentation; object detection with text prompts",
   sec_s="Paper documents detect/segment output formats as supported task prefixes - unusual and "
         "potentially useful for a VMS.",
   bench="COCO CIDEr 141.9 | VQAv2 85.6% | TextVQA 73.2%",
   bench_s="arxiv 2407.07726 - transfer-results tables. CHECK exact table numbers.  ||  "
           "IMPORTANT: these are FINE-TUNED transfer results, not zero-shot. Do not compare them "
           "directly against zero-shot numbers from other VLMs in this sheet.",
   eng="JAX/Flax, transformers, llama.cpp",
   eng_s="Big Vision JAX reference: github.com/google-research/big_vision.  ||  "
         "transformers: PaliGemmaForConditionalGeneration.  ||  llama.cpp: CHECK support state.",
   vstat="Benchmarks are FINE-TUNED not zero-shot - do not compare naively. Licence: Terms of Use.",
 ),
 dict(
   n="Moondream2 1.9B", n_s="huggingface.co/vikhyatk/moondream2 - model card title",
   lic="Apache 2.0", lic_s="huggingface.co/vikhyatk/moondream2 - model card licence field",
   tier="FULL", ctry=APACHE + " Origin: United States (Moondream / M87 Labs). "
        "NOTE: small independent vendor - assess supply-chain and maintenance risk separately from licence.",
   ctry_s=APACHE_SRC + "  ||  Vendor: moondream.ai. CONSIDER vendor longevity for a production dependency.",
   pb=1.9, p="1.86B dense (SigLIP vision + Phi-1.5-derived language)",
   p_s="huggingface.co/vikhyatk/moondream2 - model card and config.json.",
   train="Not disclosed",
   train_s="No paper published. The model card is the only primary source. This is materially weaker "
           "evidence than the other models in this sheet - flag it in review.",
   ly=24, kvh=32, hd=64, ctx="2,048",
   ctx_s="config.json max_position_embeddings = 2048. VERY LIMITING - suitable only for short "
         "single-image captioning, not for prompt-heavy work.",
   prim="Image to text - lightweight captioning and VQA for edge devices",
   prim_s="huggingface.co/vikhyatk/moondream2 model card - positioned explicitly as a small edge VLM.",
   sec="OCR; on-device deployment (only VLM here viable on Cortex-A53)",
   sec_s="Edge viability is a CALC from the 1.2 GB Q4 file size against the S50 memory budget, "
         "not a vendor claim.",
   bench="VQAv2 79.4% | TextVQA 60.2% | DocVQA 61.9%",
   bench_s="huggingface.co/vikhyatk/moondream2 - model card benchmark table. NO PAPER EXISTS. "
           "Single-source, vendor-self-reported, not independently verified. WEAKEST EVIDENCE IN THIS SHEET.",
   eng="llama.cpp, ONNX Runtime, transformers",
   eng_s="llama.cpp: GGUF builds published by the vendor.  ||  moondream.ai documents an ONNX path "
         "for edge deployment.",
   vstat="NO PAPER. Vendor-self-reported benchmarks only. Treat as indicative, not evidenced.",
 ),
]

# ---------------------------------------------------------------------------
wb = openpyxl.Workbook()

def style_header(ws, r, cols, fills):
    for i, (h, w) in enumerate(cols, start=1):
        c = ws.cell(row=r, column=i, value=h)
        c.font = Font(bold=True, size=9, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=fills[i - 1])
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = BORD
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[r].height = 44

TIER_C = {"FULL": FULL_G, "ALLY": ALLY_B, "COMMERCIAL": COMM_O, "OPEN": OPEN_P}

# =========================== SHEET 1 : SUMMARY =============================
s1 = wb.active
s1.title = "Summary"

C1 = [("Model Name", 30), ("License / Compliance", 30), ("Params", 22), ("Quantization", 13),
      ("Model Size (GB)", 13), ("Hardware Support", 52), ("CPU RAM (GB)", 12), ("VRAM (GB)", 12),
      ("Context Window", 16), ("tok/s CPU", 11), ("tok/s GPU", 11),
      ("Purpose / Category", 34), ("Benchmark / Metrics", 42), ("Inference Engines", 40)]

t = s1.cell(row=1, column=1, value="ipoefgfefs Workflow Builder - SLM Selection Summary   |   small language models only   |   full sourcing on the 'Detailed' sheet")
t.font = Font(bold=True, size=13, color="FFFFFF")
t.fill = PatternFill("solid", fgColor=HDR)
s1.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(C1))
s1.row_dimensions[1].height = 24

style_header(s1, 2, C1, [GRP] * len(C1))

HW_SHORT = ("GPU: NVIDIA CUDA sm_50+ (GTX 900 series and newer) | AMD ROCm RDNA2+ (RX 6000+) | "
            "Apple Metal M1+ .  CPU: x86-64 AVX2, ARM aarch64 NEON.  [Source: llama.cpp supported-backends doc]")

r = 3
band = False
for m in M:
    band = not band
    for q, mult in QB.items():
        fsz = round(m["pb"] * mult, 1)
        row = [m["n"], "%s  (%s)" % (m["lic"], m["tier"]), m["p"], q, fsz,
               HW_SHORT, round(fsz * 1.15, 1),
               round(fsz + kv_gb(m["ly"], m["kvh"], m["hd"], 8192), 1),
               m["ctx"], toks(fsz, False), toks(fsz, True),
               m["prim"], m["bench"], m["eng"]]
        for j, v in enumerate(row, start=1):
            c = s1.cell(row=r, column=j, value=v)
            c.font = Font(size=9)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = BORD
            if band:
                c.fill = PatternFill("solid", fgColor=ALT)
            if j == 1:
                c.font = Font(size=9, bold=True)
            if j == 2:
                c.font = Font(size=9, bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor=TIER_C.get(m["tier"], COMM_O))
                c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        r += 1
s1.freeze_panes = "B3"
s1.auto_filter.ref = "A2:%s%d" % (get_column_letter(len(C1)), r - 1)

r += 1
note = s1.cell(row=r, column=1, value=(
 "READ ME  -  CPU RAM = model file size x 1.15 (context buffers and allocator overhead).  "
 "VRAM = model weights + KV cache at an 8K context, which is the actual ipoefgfefs prompt size.  "
 "tok/s figures are CALCULATED from memory bandwidth, NOT measured on hardware - no vendor publishes them.  "
 "Every figure on this sheet has a full source citation in the matching column of the 'Detailed' sheet."))
note.font = Font(size=9, italic=True)
s1.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(C1))
s1.row_dimensions[r].height = 30

# =========================== SHEET 2 : DETAILED ============================
s2 = wb.create_sheet("Detailed")

C2 = [("Model Name", 28), ("Model Name - SOURCE", 44),
      ("Compliance - Licence", 24), ("Licence - SOURCE", 50),
      ("Compliance - Countries OK", 54), ("Countries - SOURCE", 54),
      ("Params", 24), ("Params - SOURCE", 46),
      ("Quantization", 12), ("Model Size (GB)", 12), ("Model Size - SOURCE", 46),
      ("Hardware Support", 56), ("Hardware Support - SOURCE", 62),
      ("CPU RAM (GB)", 11), ("CPU RAM - SOURCE", 42),
      ("VRAM (GB) @8K ctx", 12), ("VRAM - SOURCE", 50),
      ("Context Window", 22), ("Context Window - SOURCE", 54),
      ("tok/s CPU", 10), ("tok/s CPU - SOURCE", 48),
      ("tok/s GPU", 10), ("tok/s GPU - SOURCE", 48),
      ("Purpose / Category (PRIMARY)", 34), ("Primary Purpose - SOURCE", 50),
      ("Secondary Purpose", 40), ("Secondary Purpose - SOURCE", 50),
      ("Benchmark / Metrics", 44), ("Benchmark - SOURCE", 66),
      ("Inference Engines", 40), ("Inference Engines - SOURCE", 62),
      ("VERIFICATION STATUS", 44)]

fills = []
for h, _ in C2:
    fills.append(REFH if "SOURCE" in h else (BAD if "VERIFICATION" in h else GRP))

t = s2.cell(row=1, column=1, value="ipoefgfefs SLM Selection - DETAILED with per-cell sourcing   |   every data column is followed by its own SOURCE column   |   read the VERIFICATION STATUS column before review")
t.font = Font(bold=True, size=13, color="FFFFFF")
t.fill = PatternFill("solid", fgColor=HDR)
s2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(C2))
s2.row_dimensions[1].height = 24

style_header(s2, 2, C2, fills)

r = 3
band = False
for m in M:
    band = not band
    for q, mult in QB.items():
        fsz = round(m["pb"] * mult, 1)
        vram = round(fsz + kv_gb(m["ly"], m["kvh"], m["hd"], 8192), 1)
        row = [
            m["n"], m["n_s"],
            m["lic"], m["lic_s"],
            m["ctry"], m["ctry_s"],
            m["p"], m["p_s"],
            q, fsz, SRC_SIZE,
            hw(m["train"]), hw_src(m["train_s"]),
            round(fsz * 1.15, 1), SRC_CPURAM,
            vram, SRC_VRAM,
            m["ctx"], m["ctx_s"],
            toks(fsz, False), SRC_TOKS_C,
            toks(fsz, True), SRC_TOKS_G,
            m["prim"], m["prim_s"],
            m["sec"], m["sec_s"],
            m["bench"], m["bench_s"],
            m["eng"], m["eng_s"],
            m["vstat"],
        ]
        for j, v in enumerate(row, start=1):
            c = s2.cell(row=r, column=j, value=v)
            c.font = Font(size=8)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = BORD
            hdr = C2[j - 1][0]
            if "SOURCE" in hdr:
                c.fill = PatternFill("solid", fgColor=REFBG)
                c.font = Font(size=8, color="24292F")
            elif band:
                c.fill = PatternFill("solid", fgColor=ALT)
            if j == 1:
                c.font = Font(size=8, bold=True)
            if j == 3:
                c.font = Font(size=8, bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor=TIER_C.get(m["tier"], COMM_O))
                c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
            if j == len(C2):
                bad = ("MUST BE VERIFIED" in str(v) or "NO PAPER" in str(v)
                       or "UNKNOWN" in str(v) or "LEGAL" in str(v))
                c.fill = PatternFill("solid", fgColor=(BAD if bad else WARN))
                c.font = Font(size=8, bold=True, color=("FFFFFF" if bad else "24292F"))
        r += 1
s2.freeze_panes = "B3"
s2.auto_filter.ref = "A2:%s%d" % (get_column_letter(len(C2)), r - 1)

# ---- sourcing methodology block ------------------------------------------
r += 1
def blk(r, text, fill=SEC, size=11):
    c = s2.cell(row=r, column=1, value=text)
    c.font = Font(bold=True, size=size, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=fill)
    s2.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(C2))
    s2.row_dimensions[r].height = 20
    return r + 1

def line(r, text, bold=False):
    c = s2.cell(row=r, column=1, value=text)
    c.font = Font(size=9, bold=bold, name="Consolas")
    s2.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(C2))
    return r + 1

r = blk(r, "SOURCING METHODOLOGY - READ BEFORE REVIEW")
for t_ in [
 "EVIDENCE GRADE, strongest to weakest. Every SOURCE cell above resolves to one of these:",
 "",
 "  1. PEER-REVIEWED PAPER      arXiv ID given. Strongest evidence. Used for Phi-4, Llama 3.1, StarCoder2,",
 "                              Qwen2.5-Coder, DeepSeek-Coder-V2, Qwen2-VL, PaliGemma, LLaVA, Gemma 3, R1.",
 "  2. OFFICIAL MODEL CARD      HuggingFace card or vendor doc. This is the PRIMARY source where no paper",
 "                              exists - Granite 3.3, Phi-3.5-mini, Phi-3.5-Vision, Llama 3.2, CodeGemma.",
 "                              Not peer reviewed, but first-party and authoritative.",
 "  3. VENDOR BLOG              Official announcement. Used where the card and paper are both silent.",
 "  4. PUBLIC LEADERBOARD       NO PAPER EXISTS for the number. Third-party. Weakest published evidence.",
 "                              Applies to: Mistral 7B HumanEval (EvalPlus), part of InternVL2 (OpenCompass).",
 "  5. CALCULATED HERE          Formula stated inline in the SOURCE cell. Nothing measured on hardware.",
 "                              Applies to: model size, CPU RAM, VRAM, and ALL tok/s figures.",
 "",
 "THREE THINGS A REVIEWER SHOULD CHALLENGE FIRST:",
 "",
 "  a) tok/s is CALCULATED, NOT MEASURED. Every tok/s figure is a memory-bandwidth-bound estimate:",
 "     bandwidth x efficiency / model_size_GB. No vendor publishes tok/s and none was benchmarked here.",
 "     Real throughput depends on batch size, prompt length, KV cache pressure and the engine used.",
 "     Treat these as relative rankings between models, NOT as absolute performance commitments.",
 "",
 "  b) HARDWARE SUPPORT SPLITS INTO TWO DIFFERENT THINGS. Papers state only the hardware a model was",
 "     TRAINED on (H100, A100, TPU). No paper states what hardware can RUN the model. Inference",
 "     compatibility comes entirely from llama.cpp's supported-backends documentation. Both are given",
 "     separately in the Hardware Support column and must not be conflated.",
 "",
 "  c) 'NOT PUBLISHED' IS A FINDING, NOT A GAP. MultiPL-E C++ - the benchmark closest to the ipoefgfefs",
 "     workload - is published by only 3 of the 19 models here. Phi-4, Granite and CodeGemma never",
 "     released a C++ number. Any C++ claim about them is inference from Python HumanEval, and should",
 "     be challenged as such.",
 "",
 "CELLS MARKED 'CHECK' IN THE VERIFICATION STATUS COLUMN:",
 "",
 "  These values are correct to the best of current knowledge, but the exact table or section citation",
 "  has NOT been re-read against the source document. Before this sheet goes to architecture review,",
 "  open each cited paper and confirm the number and its table. This is flagged deliberately rather than",
 "  presenting an unverified citation as authoritative.",
 "",
 "CELLS MARKED RED - HARD BLOCKERS REQUIRING LEGAL SIGN-OFF:",
 "",
 "  - Llama 3.2 11B Vision: the Llama 3.2 licence excludes EU-domiciled entities from using the",
 "    MULTIMODAL models. If ipoefgfefs ships in Europe this is a blocker, not a caveat.",
 "  - LLaVA-1.6 13B: licence chain is LLaVA (Apache 2.0) over Vicuna over Llama 2. The effective",
 "    licence is the most restrictive link, not the top one.",
 "  - DeepSeek-Coder-V2-Lite: custom licence with an attached use-restriction policy, not Apache/MIT.",
 "  - Moondream2: no paper exists. All benchmarks are vendor-self-reported and unverified.",
 "",
 "MODEL ORIGIN vs LICENCE - THESE ARE SEPARATE QUESTIONS:",
 "",
 "  Qwen2.5-Coder, Qwen2-VL, DeepSeek and InternVL2 are China-origin. Their LICENCES (Apache 2.0/MIT)",
 "  impose no restriction whatsoever. Whether component ORIGIN matters is a procurement and policy",
 "  question - see NDAA Section 889, acquisition.gov/far/52.204-25 - and is a decision for legal and",
 "  contracts, not a technical filter. Both facts are stated in the Countries OK column; neither is",
 "  presented as overriding the other.",
]:
    r = line(r, t_)

r += 1
r = blk(r, "PRIMARY SOURCE INDEX")
r = line(r, "%-52s %-30s %s" % ("PAPER / DOCUMENT", "COVERS", "LOCATION"), bold=True)
for w, a, u in [
 ("Qwen2.5-Coder Technical Report", "Qwen2.5-Coder 7B", "arxiv.org/abs/2409.12186"),
 ("Phi-4 Technical Report", "Phi-4 14B", "arxiv.org/abs/2412.08905"),
 ("Phi-3 Technical Report", "Phi-3.5-mini, Phi-3.5-Vision", "arxiv.org/abs/2404.14219"),
 ("The Llama 3 Herd of Models", "Llama 3.1 8B", "arxiv.org/abs/2407.21783"),
 ("StarCoder 2 and The Stack v2", "StarCoder2 15B", "arxiv.org/abs/2402.19173"),
 ("DeepSeek-Coder-V2", "DeepSeek-Coder-V2-Lite", "arxiv.org/abs/2406.11931"),
 ("DeepSeek-R1", "DeepSeek-R1-Distill-Qwen-14B", "arxiv.org/abs/2501.12948"),
 ("Mistral 7B", "Mistral 7B Instruct v0.3", "arxiv.org/abs/2310.06825"),
 ("Gemma 3 Technical Report", "Gemma 3 4B", "arxiv.org/abs/2503.19786"),
 ("Qwen2-VL", "Qwen2-VL 7B", "arxiv.org/abs/2409.12191"),
 ("PaliGemma", "PaliGemma 3B", "arxiv.org/abs/2407.07726"),
 ("Improved Baselines with Visual Instruction Tuning", "LLaVA-1.5 / 1.6", "arxiv.org/abs/2310.03744"),
 ("HumanEval / Evaluating LLMs Trained on Code", "HumanEval benchmark definition", "arxiv.org/abs/2107.03374"),
 ("MultiPL-E", "MultiPL-E C++ benchmark definition", "arxiv.org/abs/2208.08227"),
 ("MMLU / Measuring Massive Multitask Understanding", "MMLU benchmark definition", "arxiv.org/abs/2009.03300"),
 ("MMMU", "MMMU benchmark definition", "arxiv.org/abs/2311.16502"),
 ("DocVQA", "DocVQA benchmark definition", "arxiv.org/abs/2007.00398"),
 ("LoRA", "Fine-tuning method", "arxiv.org/abs/2106.09685"),
 ("QLoRA", "Fine-tuning method", "arxiv.org/abs/2305.14314"),
 ("vLLM / PagedAttention", "Inference engine", "arxiv.org/abs/2309.06180"),
 ("SGLang / RadixAttention", "Inference engine", "arxiv.org/abs/2312.07104"),
 ("llama.cpp - supported backends and build docs", "ALL inference hardware support claims", "github.com/ggml-org/llama.cpp"),
 ("llama.cpp k-quants PR #1684", "ALL quantization accuracy deltas", "github.com/ggml-org/llama.cpp/pull/1684"),
 ("NVIDIA Ada GPU Architecture Whitepaper", "RTX 4090 memory bandwidth (1008 GB/s)", "nvidia.com - Ada whitepaper"),
 ("Apache License 2.0", "Licence text", "apache.org/licenses/LICENSE-2.0"),
 ("Llama 3.x Community Licence", "Licence text incl. EU multimodal clause", "llama.com/llama3_3/license"),
 ("Gemma Terms of Use", "Licence text", "ai.google.dev/gemma/terms"),
 ("BigCode OpenRAIL-M v1", "Licence text incl. flow-down duty", "bigcode-project.org/docs/pages/model-license"),
 ("DeepSeek Model Licence", "Licence text incl. use restrictions", "github.com/deepseek-ai/DeepSeek-LLM"),
 ("NDAA Section 889 / FAR 52.204-25", "Component-origin procurement rule", "acquisition.gov/far/52.204-25"),
 ("EvalPlus Leaderboard", "Mistral 7B HumanEval (no paper exists)", "evalplus.github.io/leaderboard.html"),
 ("OpenCompass Multimodal Leaderboard", "InternVL2 (partly leaderboard-sourced)", "rank.opencompass.org.cn/leaderboard-multimodal"),
]:
    r = line(r, "%-52s %-30s %s" % (w, a, u))

OUT = "/home/h412581/Downloads/ipoefgfefs_SLM_Matrix.xlsx"
wb.save(OUT)
print("saved:", OUT)
print("sheets:", wb.sheetnames)
print("Summary : %d cols x %d model-quant rows" % (len(C1), len(M) * 4))
print("Detailed: %d cols (%d data + %d source + 1 status)" % (
    len(C2), sum(1 for h, _ in C2 if "SOURCE" not in h and "VERIFICATION" not in h),
    sum(1 for h, _ in C2 if "SOURCE" in h)))
print("models:", len(M))
