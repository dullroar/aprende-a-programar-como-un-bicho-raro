# Pilot calibration of the sentence limit N

Measured by `tools/pilot_measure.py` from the PO files of the five pilot files. Prose segments only (English side of at least 6 words).

| File | English words | Spanish words | Ratio |
| --- | ---: | ---: | ---: |
| `src/forth/README.md` | 1011 | 1145 | 1.133 |
| `lessons/cs-source/concepts/recursion.md` | 299 | 351 | 1.174 |
| `lessons/study-guides/languages/forth.md` | 2981 | 3446 | 1.156 |
| `docs/curriculum.md` | 2111 | 2497 | 1.183 |
| `lessons/study-guides/languages/apl.md` | 3020 | 3488 | 1.155 |
| **Total** | **9422** | **10927** | **1.160** |

N = 25 x 1.160 = 29.0, rounded to **29**.

Spanish sentences measured: 1444. Longest 38 words, 95th percentile 22, median 6. Sentences above the measured N: 2; above 28: 3.
