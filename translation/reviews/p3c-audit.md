# P3C-016 audit: the 12 corrected files (iteration 104, 2026-11-20)

**Scope.** `docs/plan-de-estudios.md`, `lessons/cs-source/concepts/recursion.md`, `lessons/guias-de-estudio/lenguajes/apl.md`, `lessons/guias-de-estudio/lenguajes/forth.md`, `src/forth/README.md` and the seven challenge READMEs (`GoChallenge1`, `JavaChallenge1`, `KotlinChallenge1`, `LinqChallenge1`, `LinqChallenge2`, `ModernChallenge1`, `PythonChallenge1`). Rules: `translation/review-decisions-2026-11-20.md` Parts B and C.

**Result: zero critical, zero major, zero unresolved findings.** Two minor notes, both already recorded elsewhere.

## Checks run

| Check | Command | Result |
| --- | --- | --- |
| Gate runner on the 12 files | `python3 -I tools/verify.py --fast --files <the 12 files>` | OK (13 checks: lock plus 12 files; `docs/plan-de-estudios.md` is reported under its English key `docs/curriculum.md`) |
| Diagram render at 8.4 pt or more | `translation/work/render_check.py` on each of the 12 (14 diagrams in all: plan 1, recursion 1, APL 2, Forth guide 2, and 1 in each of the eight READMEs) | OK on every file |
| Link fragments | `python3 -I tools/anchors.py --check` | `anchors OK`; no `#what-the-challenge-does`, `#side-by-side` or `#gotchas-worth-knowing` left in any of the 12 files (the remaining uses are in English files still waiting for their own task) |
| Catalog build | `lessons/plan-de-estudios/build.py --check` with `BOOK_LANG=es` | internal links ok, 14 headings checked |
| Book tests in the scratch copy | `python3 -I tools/scratch_proof.py --tests` | PASS (`test_study_guides`, `test_repo_links`, `test_repo_identity`) |
| Negative fixtures | `python3 -I tools/negative.py` | control clean, 67 fixtures fail as expected, items 1 to 13 |

## Unit check on the shared challenge sentence (rule B1)

- `src/forth/README.md:21`: "agrega tarjetas de 10 a 19 horas cada una hasta que el total pase de 40". The English says "add 10 to 19 hour cards". The range now takes the unit *horas*, per card. The critical error of the review (cards instead of hours) is gone.
- `src/forth/README.md:77, 83`: "horas de 10 a 19", "un valor de 10 a 19 horas". Unit present.
- `src/JavaChallenge1/README.md:27`: "suma de 10 a 19 horas aleatorias". Unit present; the card count (five names) is not tied to the range.
- No Spanish sentence in the 12 files has "de 10 a 19" followed by *tarjetas*. The other READMEs do not state the range.

## Timecard rule check

Each README that states the stop rule says the total must **pass** 40 to stop ("no pase de 40" for the loop condition, "exactamente 40 … continúa" where the English says so: Java line 28, Modern line 82, the APL guide's *Exactamente 40* paragraph). No file says "hasta 40", "al llegar a 40" or an inclusive stop. The LINQ variants keep "exactamente 40.0 horas" as the English does.

## Regression scan on the corrected passages

- No added absolute guarantee found (`no puede dañar`, `no afecta a tu`, `nunca se publica`, `sin riesgo`, `imposible que`).
- Retired terms (`oyente`, `retrollamada`, `calcular al escribir`, `puerto de retorno`) do not occur in the prose of any of the 12 files.
- *Entorno aislado* / *sandbox* is defined once per file (verify I24 passes); the other uses are the glossed term.
- Identifiers in Mermaid labels (`also`, `step`, `where`, `from persisted in`, `let`, `over-40?`) are literal; the render check and I21 pass.

## Minor notes (no action in this task)

1. **M1: legacy path word.** `docs/plan-de-estudios.md:96` links to `10-eventos-retrollamadas-y-flujo-de-control-reactivo.md` and a guide file with the same word. The glossary bans *retrollamada* in prose, but two student-facing file names still contain it. Already recorded: `translation/decisions.md` ("Path names") and `loop/decisions-provisional.md` (iter 89); the rename is deferred to Phase 5 as a pure `git mv` plus reference rewrite. Not a finding against the 12 files.
2. **M2: English links in untranslated files.** Thirteen English study guides, `lessons/exercises.md` and others still carry `introduccion.md#what-the-challenge-does` and similar fragments. They point at headings that are still English, so they are correct today; `anchors.py --generate` plus `apply.py --relink --write` will re-aim them when those files and `introduccion.md` are translated (SIGNS rule on anchors). The Phase 3C gate (P3C-017) should confirm `anchors.py --check` still passes.

## Handed to P3C-017

`verify --release` was not run here (task scope is the 12 files). The gate task runs it and looks for path or new-rule failures on translated files only.
