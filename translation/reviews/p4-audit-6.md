# P4-audit-6 (iteration 176, 2026-11-21)

In a fresh Claude iteration, five segments were sampled from the eight completed translation tasks listed in the audit's queue record (seven language study guides and the first batch of language lessons). The draw is weighted by English length. The pool contains 1095 nonempty PO entries across 11 files. To reproduce it, sort the files by English path and the entries within each file by position, then draw with `random.Random(175).choices(range(len(pool)), weights=len_of_msgid)` until five distinct entries are chosen.

| English file and source line | Segment | Review |
| --- | --- | --- |
| `lessons/study-guides/languages/m4.md:99` | `s-5197640dd524-0052` | Pass. The table cell keeps all separators and the three code placeholders. "Un depurador", the trace options and "hace visible la profundidad al fallar" are faithful. Observation, not a finding: "`-d` flags debug output" becomes "pone una bandera en la salida de depuración", a literal calque of an ambiguous English verb. "marca la salida de depuración" would read more naturally, but the meaning survives. |
| `lessons/languages/apl.md:86` | `s-d914aadf3938-0035` | Pass. The bold sentence is kept and the logic is exact. |
| `lessons/study-guides/languages/make-and-cmake.md:168` | `s-0f4eff18c16a-0087` | Pass. The numbers (60 000 words) and "como máximo 40" are right, the exponential-backtracking warning is kept, and the code placeholder sits in the right slot. |
| `lessons/study-guides/languages/tar.md:51` | `s-bc6b79b420e1-0022` | Pass. All six code placeholders are in the right places and the list of state items is complete. The split into short sentences repeats "vive", which is acceptable under the N-word rule. Observation: "Guarda la semilla…" has the row as its implicit subject, which is a little ambiguous, but it is correct. |
| `lessons/study-guides/languages/make-and-cmake.md:21` | `s-11c6bbf7f2fd-0008` | **Finding F007 (minor).** The first use of *sandbox* is glossed only as "entorno aislado (*sandbox*)". The glossary rule B3 asks for the one-time gloss "un entorno aislado (*sandbox*) que limita el acceso al sistema anfitrión" in each file. The earlier guides (forth, apl, cobol, common-lisp, csharp) have it. All seven guides in this batch lack it. The rest of the segment is faithful: "marcados con **DEMO ONLY**" and "además" are fair clarifications. |

One finding is recorded in `translation/reviews/p4-audit-6.jsonl` and queued as review-fix task `P4-fix-7`.
