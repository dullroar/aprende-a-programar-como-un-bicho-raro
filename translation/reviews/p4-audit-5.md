# P4-audit-5 (iteration 165, 2026-11-21)

In a fresh Claude iteration, five segments were sampled from the eight completed translation tasks listed in the audit's queue record (two concept guides and six language guides). As earlier audits advised, the draw is weighted by English length. The pool contains 934 nonempty PO entries across 8 files. To reproduce it, sort the files by English path and the entries within each file by position, then draw with `random.Random(164).choices(range(len(pool)), weights=len_of_msgid)` until five distinct entries are chosen.

| English file and source line | Segment | Review |
| --- | --- | --- |
| `concepts/reading-adversarial-programs.md:145` | `s-c0ff59c3727b-0085` | Pass. All four exercises keep their bold labels, the italic answer in parentheses, the exit status 4 and the "guaranteed by design" label (*garantizado por diseño*). "Archivo tar" for "archive" is a fair clarification: the source text names tar archives throughout. Instructions use the tú imperative. |
| `languages/apl.md:178` | `s-e9fef5ea67d3-0090` | Pass. The label **permitido por la implementación** is in its frozen form. The observation about GNU APL and the workspace listing is intact. |
| `languages/forth.md:114` | `s-6b6b70cf2a87-0063` | Pass. The "exactly 40 continues" case is correct: the totals are 10, 20, 30, 40, the flag test is `40 < 41` and a fifth card is drawn. The modulo-4 category rule and the `[L29]` link are kept. |
| `languages/cobol.md:227` | `s-df56b301cb47-0120` | **Finding F005 (minor).** The label is inflected as "permitida por la implementación", which the house style forbids. The rest passes: the totals 12, 29, 40, 50 and the "exactly 40 continues" note are intact. |
| `languages/csharp-linq-xaml-and-ports.md:44` | `s-78a7d749b03d-0018` | **Finding F006 (minor).** The four card categories gain code spans that the English lacks. The rule text is faithful: "pasa de 40", "exactamente 40 continúa", 3 to 5 cards and 41 to 59 hours. |

Observation, not a finding: the COBOL segment writes "Una colega" for the English "A colleague", while the first segment in this sample (the adversarial-programs guide) writes the masculine "Un colega". The English is gender-neutral. A later consistency pass could settle on one form, so I recorded no review-fix task for it.

Two findings are recorded in `translation/reviews/p4-audit-5.jsonl` and queued as review-fix tasks `P4-fix-5` and `P4-fix-6`.
