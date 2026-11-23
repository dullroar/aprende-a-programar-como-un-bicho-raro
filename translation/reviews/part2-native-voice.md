# S7-001: native-voice read-alone pass (Part II)

Iteration 482. Scope read: root `README.md` (lines 1 to 80), `lessons/introduccion.md` (whole), code comments of `src/tcl/timecards.tcl` (lines 1 to 45), plus grep sweeps over `src/` and `lessons/`. This is a sample, not the full fixed list. Entry READMEs beyond the heading list of `src/tcl/README.md`, opening chapters and one guide per family type are NOT READ here; a later S7 pass should cover them.

Pass A (exactness and terminology) and pass B (voice, rhythm, register, humor) are reported together. Nothing was edited: every item below is a proposed `review-fix`. Source-issue items go to `translation/source-issues.md` only; none found.

## Overall

The prose reads as native, tú-imperative, with correct `¿?` and `¡!`. Logic words are exact: "pase de 40", "Un total de exactamente 40 continúa", and the three assurance labels. Humor is kept ("Claro que no.", "Haz esto en producción y estás despedido"). Code spans, macros, paths and DEMO ONLY are untouched.

## Findings

### F1 (pass A, terminology, high): "desafío" in code comments contradicts the glossary

Glossary `challenge` is `reto` and bans `desafío` (`translation/glossary.es.yaml:555-558`). Part II comment localization wrote `desafío` in 36 occurrences across 27 files under `src/`. Examples:

- `src/tcl/timecards.tcl:8`: before `# El desafío: suma tarjetas`, after `# El reto: suma tarjetas`.
- `src/tcl/timecards.tcl:23`: before `# ---- el desafío`, after `# ---- el reto`.
- `src/lisp-weird/timecards.lisp:6`: before `;;;; El desafío:`, after `;;;; El reto:`.
- `src/forth/timecards.fs:107`: before `Todo el desafío.`, after `Todo el reto.`.
- every `check.sh` line 2 of the form `Comprueba las reglas del desafío` or `Revisa las reglas del desafío`: after `... del reto`.

Reason: one approved term per concept; the root README and lessons say "reto". Fix only through `tools/loc_apply.py` (comment PO entries), with oracle proof, per Part II rules. Check COBOL first: comment lines there are capped at 72 bytes, and "reto" is shorter, so it fits.

### F2 (pass A, consistency, medium): prose calls the section **Program Flow**, the headings say "Flujo del programa"

- `lessons/introduccion.md:26`: "una sección **Program Flow**" while every entry README heading is `## Flujo del programa` (checked in `src/tcl/README.md:53`) and `CONTRIBUTING.md` links to `#flujo-del-programa-...`.
- Proposed after: "una sección **Flujo del programa**". Check `lessons/book/README.md` (lines 69 and 104 name `## Program Flow` in code spans). Those spans must stay as the build tool reads them, so verify the heading the extractor expects before touching those lines.

### F3 (pass A, title, medium): link text uses a different book title

`README.md:30`: before `**[¡Aprende a programar de la forma rara!](lessons/README.md)**`, after `**[¡Aprende a programar como un bicho raro!](lessons/README.md)**`. The edition title is `¡Aprende a programar como un bicho raro!` (README line 7 and line 5 of the same file). The English uses the same title in both places. Confirm with catalog `identity.book_title` before the fix.

### F4 (pass B, register, low): regionalism "jala"

`lessons/introduccion.md:26`: before "Un programa Haskell es una demanda que jala.", after "Un programa Haskell es una demanda que tira del resultado." Alternative: "es un cálculo dirigido por la demanda". "Jala" is mostly Mexican; the edition targets neutral es-419. Keep the English picture (pull-based).

### F5 (pass B, voice, low): "recorre en ciclo"

`lessons/introduccion.md:13`: before "recorre en ciclo Meetings, Coding, Debugging y Learning", after "recorre por turnos Meetings, Coding, Debugging y Learning" or "alterna entre". Reads stiff. The accDescr (line 18) already says "una categoría que sigue el ciclo", so changing both keeps them equal.

### F6 (pass B, typography, low): spaced hyphen as dash

`README.md:12` and `:14` use ` - ` as a parenthetical dash ("sus iteradores, ... - antes de que"). Spanish uses the raya (—) or commas. Do this only if the English uses the same dash and the house style allows it; check `translation/house-style.es.md` first. It could be a style-wide change, so treat it as a provisional decision, not a quick fix.

### F7 (pass B, cosmetic, low): comment misalignment

`src/tcl/timecards.tcl:5`: the continuation of the `Ejecuta:` example is indented one space off after localization ("tclsh timecards.tcl --gui" lines no longer align in the comment). Realign through `loc_apply` in the same task as F1 (same file).

## Not found

- No instance of "tarjetas" for the 10 to 19 hour range.
- No literal phase letters, no mixed category forms in the sampled prose. The sampled code comments keep `Meetings, Coding, Debugging, Learning` because the program still prints them (EXC-576 and sibling rows).
- No reversal of the timecard rule (strictly greater than 40 stops; exactly 40 continues).

## Disposition

Pending. Proposed review-fix groups: (1) F1 + F7 as a comment-only Part II task over 27 files with oracle proof; (2) F2, F3, F4, F5 as a PO edit of `README.md` and `lessons/introduccion.md`, then the usual `apply.py --write` and `verify.py --fast`. F6 waits for a style decision.
