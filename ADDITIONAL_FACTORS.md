# Additional SLM Selection Factors — Beyond the 13 Columns

Factors not captured in benchmarks or specs but critical for production snorkelbadger deployment.

---

## 1. Cost at Scale

**What it is:** Total cost of running the SLM across expected usage volume.

| Scenario | Cost |
|---|---|
| llama.cpp on existing server CPU | ~$0/day (hardware already there) |
| llama.cpp + RTX 3090 | ~$0/day (one-time $1,500 GPU purchase) |
| vLLM on AWS g5.xlarge (A10G) | ~$1/hr × 8 hr/day = ~$8/day |
| Groq cloud API at 50 compiles/day | ~$0.02–$0.05/compile × 50 = ~$1–2.50/day |
| Fine-tuning run (one-time) | ~$4–10 on AWS g5.xlarge (4–8 hrs) |

**snorkelbadger implication:** On-prem llama.cpp on an existing Ubuntu server costs nothing per day. Cloud API has ongoing cost and data leaves the server. Choose on-prem for privacy + cost.

---

## 2. Data Privacy / Residency

**What it is:** Where does the model process your data — on your server or someone else's cloud?

**snorkelbadger implication:** Workflow JSON files contain customer camera configurations, site maps, and watchlist logic. This may be sensitive. With llama.cpp on-prem, data never leaves the server. Cloud API (Groq, Together AI, OpenAI) sends prompt data to their servers.

**Recommendation:** On-prem only for production. Cloud API only for development/POC when prompts don't contain real customer data.

---

## 3. Concurrency

**What it is:** How many users can send compile requests simultaneously without queuing.

| Engine | Concurrent requests | Notes |
|---|---|---|
| llama.cpp (single instance) | 1 | Others wait in queue |
| llama-cpp-python with queue | 1 + queue | Simple to implement, fine for small teams |
| SGLang / vLLM | 10–50+ | Batches requests, parallel GPU processing |

**snorkelbadger implication:** For a team of 2–5 people, llama.cpp queue is fine. Nobody compiles simultaneously enough to notice. Add SGLang when the product ships to multiple customers.

---

## 4. Cold Start Time

**What it is:** How long from server boot until the SLM is ready to accept requests.

| Model | Cold start (NVMe SSD) | Cold start (HDD) |
|---|---|---|
| Phi-3.5-mini 3.8B (Q4, 2.4 GB) | ~2s | ~8s |
| Granite 3.3 8B (Q4, 4.7 GB) | ~4s | ~15s |
| Devstral 24B (Q4, 14 GB) | ~10–15s | ~45s |
| Llama 3.3 70B (Q4, 42 GB) | ~35s | ~3 min |

**snorkelbadger implication:** Load the model once at Flask startup. Keep it in memory. Never load/unload per request — that kills performance. Use NVMe SSD for model storage, not HDD.

---

## 5. Model Versioning / Reproducibility

**What it is:** Ensuring the same prompt always produces the same (or equivalent) output across deployments.

**snorkelbadger implication:**
- Pin the GGUF file by SHA256 hash, not by filename
- Same GGUF + same temperature (0.1) + same seed → deterministic output
- When updating the model, run regression tests on all 5 compile gates before deploying
- Keep the previous GGUF version for rollback

```bash
# Pin version in deployment
sha256sum devstral-small-24b-Q4_K_M.gguf > model.sha256
# Verify on deploy
sha256sum -c model.sha256
```

---

## 6. Export Control (ITAR / EAR)

**What it is:** US laws restricting export of certain technologies, including some AI models.

**snorkelbadger implication:**
- Apache 2.0 and MIT models are generally classified EAR99 (no export license needed)
- Llama community license: check §2 for export restrictions
- Camera hardware (Ambarella S50) may have its own export classification
- If snorkelbadger ships to non-US customers: have legal review the model license AND hardware EAR classification

---

## 7. Monitoring / Observability

**What it is:** Tracking model performance in production to detect degradation or failure patterns.

**Key metrics to log:**
| Metric | What to track | Alert if |
|---|---|---|
| Gate 2 pass rate | % of compiles that compile on first SLM attempt | Drops below 60% |
| Average retries | Mean feedback loop iterations per compile | Rises above 3 |
| TTFT | Time to first token per request | Exceeds 10s |
| tok/s | Output speed | Drops below 5 tok/s (server under load) |
| Error categories | Type of compile errors (type mismatch, missing include, etc.) | New error type appears frequently |

**snorkelbadger implication:** Log these in feedback_loop.py. Plot weekly. A sudden drop in gate 2 pass rate usually means the prompt template drifted from what the model expects.

---

## 8. CI/CD Integration

**What it is:** Automated testing of the SLM codegen pipeline on every code change.

**snorkelbadger test pipeline:**
```
git push → CI trigger
  → Run gen_slm_prompt.py on 5 canonical workflow.json fixtures
  → Feed each prompt to SLM (same GGUF, same temperature)
  → Run all 5 compile gates on each output
  → Assert gate pass rate ≥ 80% across fixtures
  → If pass: deploy. If fail: block merge, notify.
```

**snorkelbadger implication:** Prevents regressions when prompt templates change. Essential before fine-tuning — run this before and after FT to confirm the fine-tuned model didn't lose capability.

---

## 9. Disaster Recovery

**What it is:** What happens when the SLM server goes down or the model produces bad output.

**snorkelbadger strategy (already partially in place):**
- `feedback_loop.py` saves best output as `slm_output/BEST.cpp` — use as fallback if SLM fails
- Keep pre-compiled `.so` files for the last known good version on the camera
- Camera continues running last loaded `pipeline.so` even if server is unreachable
- Workflow builder shows "compile unavailable" UI state, doesn't crash

---

## 10. Fine-Tune Data Governance

**What it is:** Who owns the training data and can it legally be used to fine-tune?

**snorkelbadger implication:**
- Customer workflow JSONs are proprietary — get written permission before using as training data
- Synthetic data (generate workflow JSONs from templates) is safer — you own it
- Compiler errors and fixes from your own test runs = safe to use
- Check Llama 3.x license §3 — prohibits using model outputs to train competing models
- Apache 2.0 models (Granite, Devstral) have no such restriction
