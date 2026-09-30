# all-about-jev dataset

Compiled and curated by Han Xiao: [All about Jev](https://hanxiao.io/all-about-jev/) ([announcement](https://www.linkedin.com/feed/update/urn:li:ugcPost:7508930228493348865/)). All credit for the dataset goes to him; this repo only reformats it. The site's last sweep ran on 2026-09-27 UTC. We took our local copy on 2026-09-30.

The raw file is gitignored because the site publishes no licence for it. Fetch it with:

```sh
curl -sL https://hanxiao.io/all-about-jev/all-methods.jsonl -o data/all-about-jev/all-methods.jsonl
python3 scripts/build_landscape.py   # regenerates docs/landscape.md
```

The file has 2,073 entries across seven categories: app, runtime, model, benchmark, interpretation, paper and official. Each entry records findings as its source reported them; none were independently verified.
