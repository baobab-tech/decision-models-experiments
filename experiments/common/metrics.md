# Metrics

| Key | Definition | Notes |
|---|---|---|
| `accuracy` | Share of items whose top answer equals the reference label | Single-label only |
| `macro_f1` | Unweighted mean of per-class F1 | Weights rare classes equally |
| `micro_f1` | F1 over all (item, label) decisions pooled | Multi-label |
| `mean_field_score` | Unweighted mean over fields of `accuracy` (single-label fields) and `micro_f1` (multi-label fields), × 100 | Main score in experiments 01 and 02 |
| `ece_15` | Top-label expected calibration error, 15 equal-width bins | Same binning as [typed-decision-bench](../../docs/benchmarks.md) |
| `brier` | Mean squared error between the predicted distribution and the one-hot reference label | Multiclass form; lower is better |
| `nll` | Mean negative log-probability of the reference label | Probabilities clipped at 1e-12 |
| `coverage_at_5` | Share of items auto-decided when confidence is thresholded so that error on decided items is ≤5% | Threshold fitted on a held-out calibration split |
| `latency_p50_ms`, `latency_p95_ms` | Wall-clock time per request, client side | Includes network time for API runs; state batch size |
| `cost_per_1k` | USD per 1,000 decisions | API: list price at run date. Local: n/a (record hardware) |
| `tokens_per_request` | Input tokens per request as reported by the API or tokenizer | State plus question text |

- Reference labels are those of two LLMs, GLM-5.3-Flash and DeepSeek-V4.1-Flash, unless a result says otherwise. A model's score is its mean agreement with each of them; the LLM range is their agreement with each other. There is no human gold set, so scores measure agreement with LLMs, not correctness.
- Multi-label with one Noul per label: threshold each Noul at 0.5 unless the plan says otherwise. Report the threshold.
- Staged Choices (coarse then fine): the probability of a leaf label is the product of the stage probabilities.
- Report `n` and a 95% bootstrap interval (1,000 resamples) for `accuracy`, `macro_f1` and `ece_15`.
- Per-label scores ([per_label.py](per_label.py)): F1 and recall per label against each labelling LLM, averaged, next to the two LLMs' F1 against each other on that label. `macro_f1` there covers labels with at least 5 reference positives; labels with fewer positives are listed as unmeasured.
