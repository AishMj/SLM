# download_refs.py
#
# downloads every reference used in ipoefgfefs_SLM_Matrix.xlsx so we have
# offline copies to show in review. papers come down as pdf, everything
# else gets saved as html.
#
# run it like this:
#   pip install requests
#   python3 download_refs.py
#
# everything lands in a folder called refs/ next to this script.
# if something fails it just says so and carries on, it does not stop.

import os
import time
import sys

try:
    import requests
except ImportError:
    print("you need the requests library first, run: pip install requests")
    sys.exit(1)


OUTDIR = "refs"
WAIT = 1.5          # seconds between downloads so we dont hammer arxiv
TIMEOUT = 60        # give up on one file after this many seconds
RETRIES = 3         # how many times to try before giving up


# the list of everything we need.
# format is: (folder, filename, url)
# arxiv links are written as the /pdf/ form so we get the actual paper.

REFS = [

    # ---- papers ----
    ("papers", "qwen25_coder_2409.12186.pdf",        "https://arxiv.org/pdf/2409.12186"),
    ("papers", "phi4_2412.08905.pdf",                "https://arxiv.org/pdf/2412.08905"),
    ("papers", "phi3_2404.14219.pdf",                "https://arxiv.org/pdf/2404.14219"),
    ("papers", "llama3_herd_2407.21783.pdf",         "https://arxiv.org/pdf/2407.21783"),
    ("papers", "starcoder2_2402.19173.pdf",          "https://arxiv.org/pdf/2402.19173"),
    ("papers", "deepseek_coder_v2_2406.11931.pdf",   "https://arxiv.org/pdf/2406.11931"),
    ("papers", "deepseek_r1_2501.12948.pdf",         "https://arxiv.org/pdf/2501.12948"),
    ("papers", "mistral7b_2310.06825.pdf",           "https://arxiv.org/pdf/2310.06825"),
    ("papers", "gemma3_2503.19786.pdf",              "https://arxiv.org/pdf/2503.19786"),
    ("papers", "qwen2vl_2409.12191.pdf",             "https://arxiv.org/pdf/2409.12191"),
    ("papers", "paligemma_2407.07726.pdf",           "https://arxiv.org/pdf/2407.07726"),
    ("papers", "llava15_2310.03744.pdf",             "https://arxiv.org/pdf/2310.03744"),

    # ---- benchmark definitions ----
    ("benchmarks", "humaneval_2107.03374.pdf",       "https://arxiv.org/pdf/2107.03374"),
    ("benchmarks", "multipl_e_2208.08227.pdf",       "https://arxiv.org/pdf/2208.08227"),
    ("benchmarks", "mbpp_2108.07732.pdf",            "https://arxiv.org/pdf/2108.07732"),
    ("benchmarks", "evalplus_2305.01210.pdf",        "https://arxiv.org/pdf/2305.01210"),
    ("benchmarks", "canitedit_2312.12450.pdf",       "https://arxiv.org/pdf/2312.12450"),
    ("benchmarks", "cruxeval_2401.03065.pdf",        "https://arxiv.org/pdf/2401.03065"),
    ("benchmarks", "repobench_2306.03091.pdf",       "https://arxiv.org/pdf/2306.03091"),
    ("benchmarks", "mmlu_2009.03300.pdf",            "https://arxiv.org/pdf/2009.03300"),
    ("benchmarks", "gsm8k_2110.14168.pdf",           "https://arxiv.org/pdf/2110.14168"),
    ("benchmarks", "math_2103.03874.pdf",            "https://arxiv.org/pdf/2103.03874"),
    ("benchmarks", "mmmu_2311.16502.pdf",            "https://arxiv.org/pdf/2311.16502"),
    ("benchmarks", "docvqa_2007.00398.pdf",          "https://arxiv.org/pdf/2007.00398"),
    ("benchmarks", "textvqa_1904.08920.pdf",         "https://arxiv.org/pdf/1904.08920"),
    ("benchmarks", "livecodebench_2403.07974.pdf",   "https://arxiv.org/pdf/2403.07974"),

    # ---- engine / method papers ----
    ("engines", "vllm_pagedattention_2309.06180.pdf", "https://arxiv.org/pdf/2309.06180"),
    ("engines", "sglang_radixattention_2312.07104.pdf", "https://arxiv.org/pdf/2312.07104"),
    ("engines", "lora_2106.09685.pdf",               "https://arxiv.org/pdf/2106.09685"),
    ("engines", "qlora_2305.14314.pdf",              "https://arxiv.org/pdf/2305.14314"),

    # ---- model cards. these are html pages not pdfs ----
    ("model_cards", "granite_3.3_8b_instruct.html",  "https://huggingface.co/ibm-granite/granite-3.3-8b-instruct"),
    ("model_cards", "phi4.html",                     "https://huggingface.co/microsoft/phi-4"),
    ("model_cards", "phi35_mini_instruct.html",      "https://huggingface.co/microsoft/Phi-3.5-mini-instruct"),
    ("model_cards", "phi35_vision_instruct.html",    "https://huggingface.co/microsoft/Phi-3.5-vision-instruct"),
    ("model_cards", "qwen25_coder_7b_instruct.html", "https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct"),
    ("model_cards", "qwen2_vl_7b_instruct.html",     "https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct"),
    ("model_cards", "llama31_8b_instruct.html",      "https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct"),
    ("model_cards", "llama32_3b_instruct.html",      "https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct"),
    ("model_cards", "llama32_11b_vision.html",       "https://huggingface.co/meta-llama/Llama-3.2-11B-Vision-Instruct"),
    ("model_cards", "llama32_vision_card_github.html", "https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_2/MODEL_CARD_VISION.md"),
    ("model_cards", "starcoder2_15b.html",           "https://huggingface.co/bigcode/starcoder2-15b"),
    ("model_cards", "codegemma_7b_it.html",          "https://huggingface.co/google/codegemma-7b-it"),
    ("model_cards", "gemma3_4b_it.html",             "https://huggingface.co/google/gemma-3-4b-it"),
    ("model_cards", "paligemma_3b_mix_448.html",     "https://huggingface.co/google/paligemma-3b-mix-448"),
    ("model_cards", "r1_distill_qwen_14b.html",      "https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"),
    ("model_cards", "deepseek_coder_v2_lite.html",   "https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"),
    ("model_cards", "internvl2_8b.html",             "https://huggingface.co/OpenGVLab/InternVL2-8B"),
    ("model_cards", "llava_16_vicuna_13b.html",      "https://huggingface.co/llava-hf/llava-v1.6-vicuna-13b-hf"),
    ("model_cards", "moondream2.html",               "https://huggingface.co/vikhyatk/moondream2"),
    ("model_cards", "mistral_7b_instruct_v03.html",  "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3"),

    # ---- blogs and vendor docs ----
    ("blogs", "llava_next_blog.html",                "https://llava-vl.github.io/blog/2024-01-30-llava-next/"),
    ("blogs", "qwen25_coder_family_blog.html",       "https://qwenlm.github.io/blog/qwen2.5-coder-family/"),
    ("blogs", "codegemma_docs.html",                 "https://ai.google.dev/gemma/docs/codegemma"),
    ("blogs", "internvl_site.html",                  "https://internvl.github.io/"),

    # ---- token rate measurements. only source that exists for tok/s ----
    ("tokrate", "mustafa_tokens_per_sec.html",       "https://mustafa.net/llm-tokens-per-second-benchmarks/"),
    ("tokrate", "ollama_vs_llamacpp.html",           "https://markaicode.com/benchmarks/ollama-vs-llamacpp-benchmark/"),
    ("tokrate", "epyc_llm_benchmark.html",           "https://blog.leaseweb.com/2026/04/05/amd-epyc-llm-inference-benchmark-cpu-vs-gpu/"),
    ("tokrate", "llamacpp_vram_guide.html",          "https://localllm.in/blog/llamacpp-vram-requirements-for-local-llms"),
    ("tokrate", "myaihardware_benchmarks.html",      "https://www.myaihardware.com/llama-cpp-benchmarks"),

    # ---- licences ----
    ("licences", "apache_2.0.html",                  "https://www.apache.org/licenses/LICENSE-2.0"),
    ("licences", "mit_license.html",                 "https://opensource.org/license/mit"),
    ("licences", "llama33_license.html",             "https://www.llama.com/llama3_3/license/"),
    ("licences", "llama2_license.html",              "https://ai.meta.com/llama/license/"),
    ("licences", "gemma_terms.html",                 "https://ai.google.dev/gemma/terms"),
    ("licences", "bigcode_openrail_m.html",          "https://www.bigcode-project.org/docs/pages/model-license/"),
    ("licences", "far_52.204-25_ndaa889.html",       "https://www.acquisition.gov/far/52.204-25"),

    # ---- engine docs ----
    ("engine_docs", "llamacpp_repo.html",            "https://github.com/ggml-org/llama.cpp"),
    ("engine_docs", "llamacpp_kquants_pr1684.html",  "https://github.com/ggml-org/llama.cpp/pull/1684"),
    ("engine_docs", "vllm_docs.html",                "https://docs.vllm.ai/"),
    ("engine_docs", "sglang_docs.html",              "https://docs.sglang.ai/"),
    ("engine_docs", "onnxruntime_eps.html",          "https://onnxruntime.ai/docs/execution-providers/"),
]


# some sites block you if you dont look like a browser, so send a normal
# looking user agent. nothing clever here.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


def make_folders():
    # create refs/ and all the subfolders if they are not there already
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)
    for folder, name, url in REFS:
        path = os.path.join(OUTDIR, folder)
        if not os.path.exists(path):
            os.makedirs(path)


def already_have_it(path):
    # skip files we already downloaded, so you can re-run this safely
    # after your wifi drops. anything under 1kb is probably a junk file
    # or an error page so we treat it as missing and try again.
    if not os.path.exists(path):
        return False
    if os.path.getsize(path) < 1024:
        return False
    return True


def get_one(url, path):
    # try a few times, return True if it worked
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                return True, "ok (%d kb)" % (len(r.content) / 1024)

            # 403 usually means the site does not want scripts. no point
            # retrying that one, it will just fail again.
            if r.status_code == 403:
                return False, "403 forbidden, site is blocking us"

            if r.status_code == 404:
                return False, "404 not found, link may have moved"

            # anything else, wait a bit and have another go
            print("      got http %d, retrying (%d of %d)" % (r.status_code, attempt, RETRIES))
            time.sleep(3)

        except requests.exceptions.Timeout:
            print("      timed out, retrying (%d of %d)" % (attempt, RETRIES))
            time.sleep(3)

        except requests.exceptions.ConnectionError:
            print("      connection problem, retrying (%d of %d)" % (attempt, RETRIES))
            time.sleep(5)

        except Exception as e:
            # catch all so one weird url does not kill the whole run
            return False, "something went wrong: %s" % str(e)[:80]

    return False, "gave up after %d tries" % RETRIES


def main():
    print("")
    print("downloading references for ipoefgfefs_SLM_Matrix.xlsx")
    print("total files to get: %d" % len(REFS))
    print("saving into: %s/" % OUTDIR)
    print("")

    make_folders()

    done = 0
    skipped = 0
    failed = 0
    failed_list = []

    count = 0
    for folder, name, url in REFS:
        count = count + 1
        path = os.path.join(OUTDIR, folder, name)

        print("[%d/%d] %s" % (count, len(REFS), name))

        if already_have_it(path):
            print("      already downloaded, skipping")
            skipped = skipped + 1
            continue

        ok, msg = get_one(url, path)

        if ok:
            print("      %s" % msg)
            done = done + 1
        else:
            print("      FAILED - %s" % msg)
            failed = failed + 1
            failed_list.append((name, url, msg))
            # remove the empty/broken file so a re-run picks it up again
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

        time.sleep(WAIT)

    # write a little log so we know what happened
    logpath = os.path.join(OUTDIR, "download_log.txt")
    log = open(logpath, "w")
    log.write("download run finished\n")
    log.write("downloaded: %d\n" % done)
    log.write("skipped (already had): %d\n" % skipped)
    log.write("failed: %d\n\n" % failed)
    if failed_list:
        log.write("these ones did not come down, get them by hand:\n\n")
        for name, url, msg in failed_list:
            log.write("  %s\n" % name)
            log.write("    %s\n" % url)
            log.write("    reason: %s\n\n" % msg)
    log.close()

    print("")
    print("-" * 60)
    print("finished")
    print("  downloaded : %d" % done)
    print("  skipped    : %d  (already had them)" % skipped)
    print("  failed     : %d" % failed)
    print("")

    if failed_list:
        print("these failed, you will need to open them in a browser and")
        print("save the page yourself:")
        print("")
        for name, url, msg in failed_list:
            print("  %s" % name)
            print("    %s" % url)
            print("    (%s)" % msg)
        print("")
        print("note: huggingface and a few other sites sometimes block")
        print("scripts. that is normal, just save those pages manually.")
        print("")

    print("log written to %s" % logpath)
    print("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # if you ctrl-c out of it, dont dump a big ugly traceback
        print("")
        print("stopped by user. re-run the script and it will pick up")
        print("where it left off, it skips whatever it already has.")
        print("")
