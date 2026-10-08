Macro over labels with ≥5 reference positives in validation + test (900 excerpts). LLM vs LLM macro: themes 77.5, regions 93.6, methods 77.7.

| Model | Micro mean (test) | Macro themes [95% CI] | Macro regions [95% CI] | Macro methods [95% CI] |
|---|---:|---:|---:|---:|
| granite-embedding-97m-multilingual-r2-llm-nocountries-lookup | 81.4 | 76.8 [74.3, 78.5] | 84.7 [77.6, 89.8] | 76.4 [64.2, 83.5] |
| harrier-oss-v1-270m-llm-nocountries-lookup | 81.2 | 78.2 [76.1, 79.8] | 83.7 [75.6, 89.4] | 78.8 [68.8, 85.4] |
| modernbert-base-llm-nocountries-lookup | 81.0 | 77.3 [75.1, 78.9] | 84.7 [77.6, 89.7] | 77.5 [66.5, 84.6] |
| neomme-260m-llm-nocountries-lookup | 80.8 | 76.9 [74.5, 78.8] | 85.5 [77.9, 90.7] | 73.1 [60.0, 81.3] |
| gte-modernbert-base-llm-nocountries-lookup | 80.6 | 75.8 [73.5, 77.5] | 84.8 [77.6, 89.8] | 75.5 [63.9, 83.2] |
| ettin-encoder-32m-llm-nocountries-lookup | 80.4 | 75.2 [72.5, 77.1] | 83.6 [76.1, 88.9] | 77.8 [66.0, 85.7] |
| mmbert-small-llm-nocountries-lookup | 80.3 | 75.1 [72.5, 77.1] | 84.3 [76.7, 89.5] | 70.6 [55.5, 79.6] |
| ettin-encoder-150m-llm-nocountries-lookup | 80.1 | 77.4 [75.1, 79.2] | 85.2 [77.4, 90.4] | 77.6 [66.7, 84.4] |
| f2llm-v2-80m-llm-nocountries-lookup | 79.9 | 75.2 [72.5, 77.3] | 84.5 [77.4, 89.5] | 76.9 [66.3, 84.0] |
| modernjev-decide-preview-llm-nocountries-lookup | 79.7 | 72.4 [69.8, 74.2] | 85.0 [77.7, 90.0] | 73.9 [61.8, 81.8] |
| ettin-encoder-150m-llm-2tower-nocountries-lookup | 79.4 | 77.0 [74.8, 78.6] | 84.2 [77.1, 89.2] | 72.3 [57.2, 80.9] |
| lfm2.5-encoder-230m-llm-nocountries-lookup | 77.0 | 69.0 [65.6, 71.3] | 81.2 [73.7, 86.2] | 68.7 [54.0, 77.9] |
| ettin-encoder-32m-llm-nocountries-lookup-random | 77.0 | 71.5 [68.0, 73.8] | 83.6 [75.7, 88.8] | 58.8 [43.5, 69.1] |
| ettin-encoder-32m-llm-nocountries-lookup-random-n5000 | 75.6 | 67.1 [63.3, 70.0] | 83.0 [74.9, 88.3] | 46.3 [31.9, 58.5] |
| ettin-encoder-32m-llm-nocountries-lookup-random-n2500 | 72.6 | 61.8 [58.7, 63.8] | 80.2 [72.2, 85.6] | 33.9 [21.7, 45.6] |
| ettin-encoder-32m-llm-nocountries-lookup-random-n1000 | 66.3 | 45.1 [42.6, 46.9] | 73.7 [65.5, 79.0] | 31.2 [23.1, 39.1] |

Per-label F1, themes (validation + test)

| Label | Ref. positives | LLM vs LLM | ettin-encoder-32m-llm-nocountries-lookup | ettin-encoder-150m-llm-nocountries-lookup | lfm2.5-encoder-230m-llm-nocountries-lookup | ettin-encoder-32m-llm-nocountries-lookup-random-n1000 | ettin-encoder-32m-llm-nocountries-lookup-random-n2500 | ettin-encoder-32m-llm-nocountries-lookup-random-n5000 | ettin-encoder-32m-llm-nocountries-lookup-random | granite-embedding-97m-multilingual-r2-llm-nocountries-lookup | mmbert-small-llm-nocountries-lookup | f2llm-v2-80m-llm-nocountries-lookup | modernbert-base-llm-nocountries-lookup | modernjev-decide-preview-llm-nocountries-lookup | gte-modernbert-base-llm-nocountries-lookup | ettin-encoder-150m-llm-2tower-nocountries-lookup | harrier-oss-v1-270m-llm-nocountries-lookup | neomme-260m-llm-nocountries-lookup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| education | 182 | 93.2 | 89.6 | 92.7 | 91.1 | 81.1 | 87.0 | 90.1 | 90.5 | 93.2 | 92.5 | 93.4 | 92.9 | 91.5 | 93.1 | 93.0 | 94.4 | 94.4 |
| governance | 158 | 69.2 | 73.8 | 72.6 | 66.2 | 60.1 | 66.2 | 68.9 | 70.1 | 74.4 | 74.7 | 70.9 | 73.4 | 69.7 | 72.2 | 72.7 | 72.6 | 75.3 |
| humanitarian | 143 | 92.3 | 89.2 | 88.4 | 90.3 | 81.4 | 81.5 | 86.4 | 84.9 | 90.1 | 90.3 | 90.1 | 89.1 | 90.1 | 92.3 | 89.3 | 91.7 | 90.6 |
| gender_equalities | 132 | 90.6 | 91.0 | 92.2 | 90.3 | 71.2 | 86.3 | 87.9 | 91.2 | 93.1 | 91.4 | 91.1 | 92.4 | 89.9 | 92.3 | 91.8 | 91.8 | 92.0 |
| social_development | 131 | 80.2 | 74.8 | 78.5 | 75.5 | 56.5 | 66.7 | 71.2 | 73.0 | 79.3 | 77.8 | 77.0 | 79.9 | 75.7 | 80.6 | 80.0 | 82.3 | 81.6 |
| economic_development | 115 | 75.7 | 67.2 | 75.9 | 66.5 | 67.0 | 71.8 | 69.4 | 71.8 | 69.5 | 74.9 | 73.8 | 71.6 | 66.6 | 67.9 | 72.8 | 78.8 | 77.3 |
| global_health | 112 | 92.4 | 84.8 | 88.5 | 86.9 | 66.7 | 79.4 | 85.2 | 85.7 | 90.3 | 84.3 | 88.0 | 89.5 | 81.5 | 88.3 | 90.2 | 88.3 | 88.2 |
| food_agriculture | 62 | 95.9 | 80.8 | 89.0 | 74.7 | 76.3 | 76.6 | 83.1 | 76.9 | 89.0 | 87.6 | 81.0 | 84.7 | 82.9 | 85.0 | 85.0 | 93.2 | 88.1 |
| information_digital | 54 | 82.6 | 83.3 | 80.0 | 56.4 | 10.7 | 51.8 | 78.1 | 75.6 | 85.7 | 67.0 | 83.8 | 75.1 | 77.0 | 81.6 | 83.3 | 83.7 | 83.4 |
| climate | 54 | 90.7 | 86.3 | 90.4 | 85.9 | 71.1 | 83.0 | 84.7 | 83.2 | 86.0 | 86.6 | 87.4 | 90.0 | 80.8 | 84.8 | 88.3 | 88.6 | 87.8 |
| conflict | 44 | 77.3 | 63.6 | 64.1 | 67.1 | 24.9 | 53.0 | 63.1 | 65.6 | 64.7 | 69.4 | 66.1 | 72.6 | 57.8 | 56.5 | 68.2 | 68.1 | 67.8 |
| global_partnerships | 42 | 36.1 | 48.9 | 46.8 | 40.5 | 41.9 | 40.9 | 43.2 | 47.5 | 48.4 | 50.5 | 45.2 | 45.0 | 46.1 | 47.1 | 48.5 | 49.0 | 49.9 |
| civil_society | 40 | 65.0 | 62.8 | 66.3 | 64.3 | 28.2 | 46.9 | 52.2 | 61.5 | 65.4 | 60.2 | 63.4 | 66.7 | 56.5 | 61.9 | 63.2 | 64.3 | 67.9 |
| science_technology | 16 | 6.1 | 26.9 | 28.8 | 13.2 | 0.0 | 0.0 | 6.1 | 25.2 | 15.8 | 20.5 | 34.5 | 17.9 | 6.1 | 8.8 | 8.8 | 16.2 | 15.4 |
| infrastructure | 16 | 68.8 | 66.7 | 74.5 | 58.6 | 0.0 | 72.2 | 62.4 | 72.8 | 72.8 | 64.3 | 69.7 | 73.9 | 70.4 | 71.5 | 76.4 | 73.8 | 68.1 |
| migration | 12 | 78.3 | 78.9 | 74.8 | 66.0 | 0.0 | 66.1 | 39.7 | 64.1 | 78.4 | 69.3 | 71.3 | 76.6 | 74.2 | 81.0 | 79.2 | 81.6 | 66.9 |
| energy | 11 | 100.0 | 90.9 | 95.7 | 69.0 | 0.0 | 0.0 | 42.9 | 53.3 | 100.0 | 95.7 | 91.7 | 100.0 | 91.7 | 100.0 | 100.0 | 100.0 | 100.0 |
| growth | 9 | 100.0 | 94.7 | 94.7 | 80.0 | 75.0 | 82.4 | 94.1 | 94.1 | 85.7 | 94.7 | 76.2 | 100.0 | 94.1 | 100.0 | 94.7 | 90.0 | 90.0 |

Per-label F1, methods (validation + test)

| Label | Ref. positives | LLM vs LLM | ettin-encoder-32m-llm-nocountries-lookup | ettin-encoder-150m-llm-nocountries-lookup | lfm2.5-encoder-230m-llm-nocountries-lookup | ettin-encoder-32m-llm-nocountries-lookup-random-n1000 | ettin-encoder-32m-llm-nocountries-lookup-random-n2500 | ettin-encoder-32m-llm-nocountries-lookup-random-n5000 | ettin-encoder-32m-llm-nocountries-lookup-random | granite-embedding-97m-multilingual-r2-llm-nocountries-lookup | mmbert-small-llm-nocountries-lookup | f2llm-v2-80m-llm-nocountries-lookup | modernbert-base-llm-nocountries-lookup | modernjev-decide-preview-llm-nocountries-lookup | gte-modernbert-base-llm-nocountries-lookup | ettin-encoder-150m-llm-2tower-nocountries-lookup | harrier-oss-v1-270m-llm-nocountries-lookup | neomme-260m-llm-nocountries-lookup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rct | 96 | 94.3 | 94.6 | 92.1 | 90.5 | 75.2 | 82.9 | 87.3 | 90.2 | 96.2 | 94.7 | 94.1 | 94.7 | 94.6 | 94.1 | 91.8 | 94.2 | 95.1 |
| quantitative_longitudinal | 16 | 62.5 | 76.9 | 70.3 | 57.6 | 26.5 | 16.4 | 34.0 | 45.2 | 70.0 | 56.4 | 69.0 | 70.7 | 68.5 | 65.1 | 65.7 | 70.7 | 61.7 |
| case_based | 9 | 66.7 | 53.8 | 62.5 | 60.0 | 0.0 | 18.2 | 41.7 | 60.0 | 62.5 | 64.7 | 58.8 | 58.8 | 55.6 | 57.1 | 62.5 | 64.7 | 58.8 |
| difference_in_difference | 8 | 87.5 | 85.7 | 85.7 | 66.7 | 23.1 | 18.2 | 22.2 | 40.0 | 76.9 | 66.7 | 85.7 | 85.7 | 76.9 | 85.7 | 69.2 | 85.7 | 76.9 |
