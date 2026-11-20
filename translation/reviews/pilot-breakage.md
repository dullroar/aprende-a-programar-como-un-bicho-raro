# Pilot breakage copies (plan Appendix A, step 7; task P3-008)

`python3 -I tools/breakage_pilot.py` breaks the five translated pilot files in throwaway copies (in memory, or under
`translation/work/negative/`, git-ignored) and asks the functions that `verify.py --release` calls whether they notice.
The control (the pilot files as committed) is clean first. `verify.py --release` runs it as part of
"negative fixtures" next to the synthetic catalog of `tools/negative.py`.

| Step | Copies | Caught by |
|---|---|---|
| a. stop rule weakened | README "pase de 40" becomes "llegue a 40"; guide "no pasa de 40" becomes "es menor que 40"; APL label `total ≤ 40` becomes `total < 40`; APL code span `40≥` becomes `40>` | I7 banned stop wording (2), I3 comparison sign, I13 code span |
| b. one byte of a frozen file | `src/forth/timecards.fs`, `src/forth/check.sh` (mini repo with the real file and manifest row) | I13 lock |
| c. accDescr deleted | one per pilot file (5), plus the curriculum accDescr left in English | I5, I9 |
| d. Spanish heading anchor broken | a link fragment translated to Spanish where the target heading is still English (two files); a heading renamed in the finished file | I4 and anchors.check_links; I16 |
| e. English phase letter survives (the `W` repeat) | bare `W` in prose (2), `W:` label, `fase = W`, the English acronym | I14 |

20 copies, all fail; the control is clean.

## What the breakage found (real defects, fixed in this task)

1. **A surviving English phase letter in the committed pilot.** `docs/curriculum.md` said "vuelve a empezar en W" and
   "La W es recursiva" (the third was the exercise section D, a legitimate letter). I14 only caught labels such as
   `W:` and `fase = W`, not a bare letter. New I14 rule: a bare English phase letter that the source also wrote bare
   and the Spanish kept is refused (letters that start exercise IDs are skipped as ambiguous). The two PO entries now
   use `{{phase.1.letter}}`; the file was regenerated.
2. **The stop rule could be reworded with a verb the ban list did not know.** "llegue a 40", "llegar a 40", "alcance 40",
   "alcanzar 40" and "menor que 40" are now banned stop wording (glossary `frozen.timecard_rule.banned`).
3. **A comparison sign could change in a label.** `total ≤ 40` became `total < 40` with no check failing. I3 now refuses a
   comparison sign (`≤ ≥ < > ≠`, with `<=` and `>=` normalized) that the Spanish has more often than the source;
   putting the sign in words stays allowed.

## Known limit (not a gate)

A paraphrase that flips a boundary without a banned phrase or a sign ("Es verdadera para 40" becomes "Es falsa para 40")
passes every deterministic check. That class is the job of the reviewer; the seeded-fault recall test
(`translation/reviews/pilot-recall.md`) caught 10 of 10 such flips.
