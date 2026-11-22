# P4-audit-8 (iteration 353, 2026-11-22)

In a fresh Claude iteration, five segments were sampled from the completed translation tasks in the audit's queue record (blocking-problems, exercises, front matter, goals, intro, patterns, problems-overcome, the tools README and the three docs files). The pool contains 912 nonempty PO entries across 11 files. To reproduce it, sort the files by English path and the entries within each file by position, then draw with `random.Random(353).choices(range(len(pool)), weights=len_of_msgid)` until five distinct entries are chosen.

| English file and source line | Segment | Review |
| --- | --- | --- |
| `docs/curriculum.md:144` | `s-8f93b9f61614-0100` | Pass. Bold lead and the two imperatives are faithful; tú form used. |
| `lessons/exercises.md:170` | `s-3fbbc294c814-0080` | Pass. The three engines and their three outcomes are kept in order; the code slot is in place. |
| `lessons/patterns.md:15` | `s-79faa4c41db4-0009` | Pass. Table cells and separators intact; "etapas perezosas e inmediatas" is faithful for lazy and eager. |
| `lessons/front-matter.md:12` | `s-e8adbd14807f-0001` | Pass. All 19 HTML slots and the macro are in place; the license text is complete and keeps the capitalized warranty paragraph. |
| `lessons/exercises.md:219` | `s-ede28ff343e9-0105` | Pass. Three steps and all code and link slots kept; "cadena de texto SQL" is slightly heavy but unambiguous (observation only). |

No findings; no review-fix tasks queued.
