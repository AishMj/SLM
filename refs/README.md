# refs/ - offline copies of every source cited in ipoefgfefs_SLM_Matrix.xlsx

Downloaded 2026-08-10 by `download_refs.py` so sources can be produced in review
without depending on a live link.

| Folder | Contents |
|---|---|
| `papers/` | 18 arXiv PDFs - the model technical reports |
| `benchmarks/` | 14 arXiv PDFs - benchmark definitions (what each metric measures) |
| `engines/` | 4 arXiv PDFs - vLLM, SGLang, LoRA, QLoRA |
| `model_cards/` | 28 HuggingFace pages - PRIMARY source where no paper exists |
| `blogs/` | 7 vendor blogs and reference repos |
| `tokrate/` | 5 pages - the ONLY published source for tokens/sec |
| `engine_docs/` | 5 pages - llama.cpp, vLLM, SGLang, ONNX Runtime |
| `licences/` | 8 licence texts |

86 of 88 downloaded. `download_log.txt` lists what failed.

## Two things to know before citing from this folder

**1. The Llama 3.2 EU multimodal clause is NOT in the LICENSE file.**

`licences/llama32_license.txt` is the complete LLAMA 3.2 COMMUNITY LICENSE AGREEMENT
pulled from Meta's own GitHub repo. It runs to Section 7 (Governing Law) and contains
**zero** occurrences of "European Union", "domiciled" or "multimodal".

The EU restriction lives on the **model card**, not in the licence agreement. It is
present in `model_cards/llama32_11b_vision.html` and `model_cards/llama32_3b_instruct.html`,
worded:

> "With respect to any multimodal models included in Llama 3.2, the rights granted under
> Section 1(a) of the Llama 3.2 Community License Agreement are not being granted to you
> if you are an individual domiciled in, or a company with a principal place of business
> in, the European Union."
>
> "This restriction does not apply to end users of a product or service that incorporates
> any such multimodal models."

Anyone reviewing only the LICENSE file would conclude there is no EU restriction. There is.
Cite the model card, not the licence, when raising this point.

**2. Two files failed to download and are not here.**

`llama.com/llama3_3/license` and `ai.meta.com/llama/license` both return HTTP 400 to
scripts. Save them from a browser if the rendered pages are needed. The substantive text
is already covered by `licences/llama32_license.txt` plus the model cards above.

## Redaction note

Three of the downloaded pages contained API keys embedded in the page source by the
site owners. GitHub secret scanning flagged them on push.

| File | What | Whose |
|---|---|---|
| `blogs/codegemma_docs.html` | 9 Google API keys | Google's, in ai.google.dev page JS |
| `licences/gemma_terms.html` | same 9 Google keys | Google's, same site |
| `blogs/internvl_site.html` | 1 AWS access key ID | third party, in the InternVL page |

**None of these are ipo credentials.** The Google ones are browser-side, domain-restricted
keys that Google publishes deliberately in its own developer docs. They arrived here only
because `download_refs.py` saved the raw HTML.

All 19 occurrences have been replaced with `[REDACTED-...]` placeholders and the commit that
introduced them was rewritten out of history, so they are not recoverable from this repo.
The pages remain usable as evidence - the keys were page furniture, not content.

If you re-run `download_refs.py`, these keys will come back down. Re-run the redaction, or
just do not commit `refs/` again.
