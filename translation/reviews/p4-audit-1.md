# P4-audit-1 (iteration 112, 2026-11-21)

**Scope.** Five finished segments sampled (python `random.seed(112)` over `translation/po/src/*/README.md.po`, segments longer than 60 characters with no code placeholder; script `translation/work/audit1_sample.py`) from the READMEs of P4-src-1 to P4-src-8. Each was compared with the English and, where needed, with the source code it describes.

**Result: 0 critical, 0 major, 2 minor, 1 nit.** Two review-fix tasks created (P4-fix-1, P4-fix-2); the nit is recorded only.

| # | File and segment | Verdict |
| --- | --- | --- |
| 1 | `src/awk-weird/README.md:131`, `s-d2858e512e35-0057` | **A1, minor.** See below. |
| 2 | `src/LinqChallenge2/README.md:60`, `s-a296386aacb3-0023` (diagram label) | **N1, nit.** Faithful; identifiers `let window`, `let pulse` and `void` kept. "cada una, una consulta" reads slightly choppy; no change required. |
| 3 | `src/javascript-events/README.md:122`, `s-3005680d4c70-0053` | OK. Italics, logic ("ahora" vs "en un turno posterior") and meaning preserved. |
| 4 | `src/JavaChallenge1/README.md:127`, `s-700000841a72-0064` (table header) | OK. Separators intact; "interfaz local" follows the binding decision for *loopback*. |
| 5 | `src/ex-weird/README.md:122`, `s-241bc880d31d-0051` (table row) | OK. "cinco dígitos", "sustitución", command preserved. |

## A1 (minor): "más" turns a join into a sum

- English: "**The run id** is the epoch seconds and the awk's process id."
- Spanish: "**El id de ejecución** es los segundos de época más el id de proceso de awk."
- Code (`src/awk-weird/timecards.awk:31`): `run = systime() "-" PROCINFO["pid"]`. The two values are joined as text with a hyphen, not added. "más" invites the reader to expect an arithmetic sum, which the English "and" does not. The subject-verb agreement is also off ("El id ... es los segundos"). Suggested: "El id de ejecución son los segundos de época y el id de proceso de awk, unidos con un guion" only if the added detail is already in the English; otherwise just "...son los segundos de época y el id de proceso de awk."

## A2 (minor, found while checking the awk entry README): two renderings of one English sentence

`src/awk/README.md` line 3 (front matter `teaches:`) says "variables locales de parámetro para el estado"; line 17 (**Te enseña:**) says "variables locales declaradas como parámetros para el estado". The English is identical in both places ("parameter-local variables for state"), so the Spanish should be too (SIGNS: keep `teaches` and `Te enseña:` identical in meaning). The body text (line 70) uses "variables locales en la lista de parámetros". The fix should pick one phrase and use it in both places, and the same phrase in the `state:` line and the diagram label if they repeat it.

## Checks run

- `python3 -I tools/verify.py --fast`: OK.
- No timecard-rule, unit or absolute-guarantee issues in the five sampled segments.

## Process note

The sample is small by design. A1 and A2 are both inconsistency or precision slips the deterministic gates do not catch (a repeated English sentence rendered two ways; a connective that changes the operation). Later translators should check connectives against the code that the sentence describes.
