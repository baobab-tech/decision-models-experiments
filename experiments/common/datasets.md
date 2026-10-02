# Datasets

## In use: evaluation docs

Used by experiments 01 and 02.

| | |
|---|---|
| Source | 1,420 international development evaluation reports from about 40 organisations, converted with Docling, plus labels from an LLM ingestion pipeline. Built from `baobabtech/evalexplorer-data` (private) |
| Dataset | [`baobabtech/decision-models-evaluation-docs`](https://huggingface.co/datasets/baobabtech/decision-models-evaluation-docs) (public): configs `documents`, `excerpts` (with the fixed 600-excerpt `eval_sample`) and `taxonomy` (labels, definitions, country→region). Built by [`build_evaluation_docs_dataset.py`](build_evaluation_docs_dataset.py) from source revision `3543e3e` |
| Splits | By document, 80/10/10 (1,148 / 138 / 134), identical across configs |
| Labels | LLM output (Gemini 2.5 Flash, gpt-oss-120b, Qwen 3 235B) treated as gold; 36 document labels corrected by hand |
| Licence | Reports are publicly published by their organisations, which keep their rights; the dataset card says `other` |
| Version | Record the HF commit of `decision-models-evaluation-docs` |

## Candidates, not in use

Public datasets kept for later experiments. Licences are as stated by the source; unconfirmed entries are marked (unverified).

| Dataset | Labels | Type | Typical length | Licence | Reports are publicly published by their organisations, which keep their rights; the dataset card says `other` |
|---|---:|---|---|---|---|---|
| BANKING77 | 77 | single | ~12 words | CC-BY-4.0 (HF card, checked 2026-09-30; mirrors `legacy-datasets/banking77` CC-BY-4.0, `mteb/banking77` card says MIT) | [HF `PolyAI/banking77`](https://huggingface.co/datasets/PolyAI/banking77) | many-class intent; AnyJev and CLM-8B report on it |
| CLINC150 | 150 + out-of-scope | single | ~9 words | CC-BY-3.0 (repo LICENSE and HF `clinc/clinc_oos` card, checked 2026-09-30) | [clinc/oos-eval](https://github.com/clinc/oos-eval) | abstention on out-of-scope |
| DBpedia classes (L1/L2/L3) | 9 / 70 / 219 | single, hierarchical | ~50–100 tokens | Kaggle listing: CC0 (uploader's label); DBpedia source data CC-BY-SA-3.0 (HF `fancyzhx/dbpedia_14` card); checked 2026-09-30 | [Kaggle "DBPedia Classes"](https://www.kaggle.com/datasets/danofer/dbpedia-classes) | staged Choices on a hierarchy |
| 20 Newsgroups | 20 | single | ~300–2,000+ tokens | not stated by scikit-learn or the SetFit HF mirror (checked 2026-09-30; unverified) | [scikit-learn loader](https://scikit-learn.org/stable/datasets/real_world.html#newsgroups-dataset) | long inputs |
| Reuters-21578 (ModApte) | 90 | multi | ~100–1,000 tokens | CC-BY-4.0 (UCI page, checked 2026-09-30) | [UCI](https://archive.ics.uci.edu/dataset/137/reuters+21578+text+categorization+collection) | news topic tags |
| AgentToolDecisions-180K | 2–32 per row (6 task families) | single (Choice) and Noul | agent conversation + tool list | `other`: mixed CC BY 4.0, Apache 2.0, MIT per row (card, checked 2026-10-02; unverified) | [HF `MaziyarPanahi/AgentToolDecisions-180K`](https://huggingface.co/datasets/MaziyarPanahi/AgentToolDecisions-180K), revision `22b9113` | agent tool routing; each row has a ready Jev request; trained [ModernJEV-Decide-Preview](../../docs/models/modernjev-decide.md) |
| Document types | ~10–30 | single | ~500–2,000 tokens | TBD | TBD: public collection or synthetic | report, invoice, contract, … |

Record the exact version: HF commit hash, file checksum or download date.
