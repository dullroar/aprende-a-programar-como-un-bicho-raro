# P4-audit-2 (iteration 125, 2026-11-21)

In a fresh Codex iteration, five segments were sampled from the eight completed translation tasks listed in the audit's queue record. The pool contains 1,140 non-obsolete, nonempty, non-fuzzy PO entries across 17 files. To reproduce the draw, sort the files by English path and the entries within each file by `msgctxt`, then take `random.Random(125).sample(pool, 5)` in Python.

| English file and source line | Segment | Review |
| --- | --- | --- |
| `src/regex-pcre2/README.md:112` | `s-1edc8bb51840-0047` | Minor (F003). The subject of "nunca ocurre" is unclear. The English says the total cannot still be 40 or less after five cards. Four cards of 10 hours reach 40 and continue, and five reach 50. The `gate` callout tests `d->total > 40`. |
| `src/regex-dotnet/README.md:104` | `s-3092f522323b-0044` | Minor (F004). "que construyó la expresión regular" can read as if the stack built the expression. In `Program.cs:13` the expression adds an `s` capture for each hour. The per-row `hrs` lengths are correctly described. |
| `src/regex-perl/README.md:96` | `s-3995b3cb87ef-0042` | Pass. The test summary keeps the one-statement constraint, the printed text, the hours per card, the strict stop, the exactly-40 case and the SQLite requirements. |
| `src/m4/README.md:71` | `s-dbf9c806efc3-0029` | Pass. The heading preserves the literal name `m4` and the promise of one paragraph. |
| `src/regex-sed/README.md:165` | `s-91b49190e85b-0070` | Pass. The heading preserves the step number and names both the start of the loop and the stop rule. |

The sample yielded two minor findings and no major or critical findings. The [finding records](p4-audit-2.jsonl) are queued as `P4-fix-3` and `P4-fix-4`. The Phase 4 gate depends on both.
