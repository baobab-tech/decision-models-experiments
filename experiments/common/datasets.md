# Datasets

Candidates for experiments 01 and 02. Licences are as stated by the source. Confirm each one before the dataset is used; unconfirmed entries are marked (unverified). API-only models get public datasets only (see [AGENTS.md](../../AGENTS.md)).

| Dataset | Labels | Type | Typical length | Licence | Source | Used for |
|---|---:|---|---|---|---|---|
| BANKING77 | 77 | single | ~12 words | CC-BY-4.0 (HF card, checked 2026-09-30) | [HF `PolyAI/banking77`](https://huggingface.co/datasets/PolyAI/banking77) | many-class intent; AnyJev and CLM-8B report on it |
| CLINC150 | 150 + out-of-scope | single | ~9 words | CC-BY-3.0 (repo LICENSE, checked 2026-09-30) | [clinc/oos-eval](https://github.com/clinc/oos-eval) | abstention on out-of-scope |
| DBpedia classes (L1/L2/L3) | 9 / 70 / 219 | single, hierarchical | ~50–100 tokens | CC-BY-SA-3.0 (unverified) | [Kaggle "DBPedia Classes"](https://www.kaggle.com/datasets/danofer/dbpedia-classes) | staged Choices on a hierarchy |
| 20 Newsgroups | 20 | single | ~300–2,000+ tokens | not stated; commonly used for research (unverified) | [scikit-learn loader](https://scikit-learn.org/stable/datasets/real_world.html#newsgroups-dataset) | long inputs |
| Reuters-21578 (ModApte) | 90 | multi | ~100–1,000 tokens | free for research; see the collection's README (unverified) | [UCI](https://archive.ics.uci.edu/dataset/137/reuters+21578+text+categorization+collection) | news topic tags |
| Document types | ~10–30 | single | ~500–2,000 tokens | TBD | TBD: public collection or synthetic | report, invoice, contract, … |

Record the exact version: HF commit hash, file checksum or download date.
