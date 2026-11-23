# Part II, S0 gate (S0-004)

Exit criteria (plan, Phase S0): every protected file classified exactly once; the matrix complete; the real language list reconciled against the second-pass plan's hypothesis table; existing failures recorded honestly.

## 1. Classification: every protected file exactly once

Checked by reading `translation/part2/code-inventory.jsonl` against `translation/locked-code.sha256`:

- 230 locked paths, 230 inventory records, 230 distinct paths, and the two sets are equal.
- Every record has a non-empty `host` and a `family`; none is unclassified.

Families by entry (file counts): 32 Linux `src/` entries (apl 3, apl-weird 3, awk 3, awk-weird 3, cmake 3, cobol 4, cobol-weird 4, ed-weird 5, ex-weird 4, find-gnu 4, find-posix 4, forth 3, forth-weird 3, haskell 3, haskell-weird 3, javascript 4, javascript-events 5, javascript-weird 6, lisp 3, lisp-weird 3, m4 3, make-gnu 3, regex-dotnet 5, regex-pcre2 5, regex-pcre2grep 3, regex-perl 3, regex-sed 5, tar-gnu 7, tar-gnu-weird 8, tcl 3, tcl-weird 3); 9 Windows/GUI entries (GoChallenge1 6, JavaChallenge1 12, KotlinChallenge1 12, LinqChallenge1 5, LinqChallenge2 5, ModernChallenge1 4, PythonChallenge1 3, RustChallenge1 6, xaml 7); `lessons/solutions` (awk-port 3, b7-linq 2, two single files, 12 further files under `lessons/`); `sandbox/` 21; root build and repo files (Gradle wrapper and settings, `.gitattributes`, `.github`, `LICENSE`).

The English `LICENSE` and the repo files are never localizable (plan 4.5.1); they stay frozen whatever the matrix says.

## 2. Matrix complete

`translation/part2/runtime-matrix.md` has a row for every `src/` entry (32), every Windows/GUI entry (9) and every solution (4). Totals there: 28 Linux entries PASS-capable (unproven) and 4 NOT TESTED; all 9 Windows/GUI entries NOT TESTED; 1 solution PASS-capable and 3 NOT TESTED.

**Open and not hidden:** the sandbox self-test was NOT RUN and no tool version was read, because Docker calls are refused in `claude -p` dontAsk mode. "PASS-capable" therefore means "a trusted image and a `check.sh` exist", not "verified". A Docker-capable session must run `sandbox/selftest.sh` and read versions before any family moves from `frozen` (S1 starts everything frozen anyway, and S5 may not localize an entry whose oracle cannot run).

## 3. Real language list versus the second-pass plan's hypothesis table

**Limit of this reconciliation:** the second-pass plan (`plan-segunda-pasada-espanol-bicho-raro.md`) is not in this repository or on this machine; the synthesized plan only summarizes it ("a language matrix of about 25 families and a checker/CI file list", section 0.4). A cell-by-cell comparison was therefore impossible. What follows compares the measured list with that summary and states the measured list as the new authority, so S1 can build one registry per entry here.

Measured (inventory, 35 host languages across 230 files): apl 2 files, awk 3, batch 3, binary 4, c 1, cmake 1, cobol 2, csharp 14, data 7, dockerfile 39, ed 1, ex 1, forth 2, gitconfig 14, go 2, gradle 6, haskell 3, java 3, javascript 10, json 3, kotlin 3, lisp 2, m4 1, makefile 2, perl 1, powershell 9, properties 5, python 3, rust 3, sed 1, shell 65, sql 2, tcl 2, toml 1, xml 9. Embedded: SQL 288 occurrences, regex 24, shell 2, text 2.

Findings against the hypothesis (about 25 families):

- The measured count is higher: 35 host-language labels plus 4 embedded kinds. The difference is mostly non-program hosts the hypothesis likely did not count: dockerfile (39 files), gitconfig (14), properties, toml, json, xml, binary, data and powershell. These carry mostly contract text and stay frozen by default.
- Shell is the largest host (65 files), mostly sandbox and `check.sh` scripts; it is a contract surface, not a teaching surface.
- Two labels are ambiguous by extension and are resolved by path: `.fs` is Forth under `src/forth*` (not F#); `.bat` files hash after CRLF to LF.
- Embedded SQL (288) and regex (24) need their own registries (S1 batch 3), which the hypothesis list may have filed as separate families.
- Not found in this repository: any F#, Ruby, PHP, Swift or TypeScript file, if the hypothesis included them (unverifiable without the document; treat as not present).
- Unmeasured: the checker/CI file list. Here the CI surface is one file under `.github/` and the 21 files under `sandbox/`.

Decision: the registry list for S1 is the measured list above; a later task may add a language only if a protected file is found that uses it (`tools/code_inventory.py` is the detector).

## 4. Existing failures, recorded honestly

- Sandbox self-test: NOT RUN (Docker refused in dontAsk mode). No tool version was read from a running container.
- No entry has been executed, English or Spanish; no oracle exists yet (S2-004).
- NOT TESTED by the matrix: 4 Linux entries (cobol, haskell, regex-pcre2, regex-perl), all 9 Windows/GUI entries and 3 of 4 solutions (see matrix).
- Inventory roles and string classes are provisional hints, not decisions; the registries and the scope file decide.
- Part I gate P4-999 passed only under re-scoped criteria (see `loop/log.md`, iterations 374 and 376); that history is unchanged here.
- No protected file was changed by this task.

## Gate result

S0 passes as a gate on classification and matrix completeness. The self-test and tool versions remain owed to a Docker-capable session, and the hypothesis table could not be compared cell by cell because the source document is absent.
