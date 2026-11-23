# Part II policy (S1-001): plan 4.5.1 to 4.5.3 as testable rules

Source: plan section 4.5. Each rule has an id, a check, and who enforces it. "Task" means a `localize-code` task of Phase S5. Scope file: `translation/localization-scope.yaml` (all 53 families `frozen` at S1).

## A. Protection classes (4.5.1), decided per occurrence by role

| Id | Rule | Test |
| --- | --- | --- |
| P-01 | Language syntax and operators never change. | Token diff outside mapped spans is empty (I29). |
| P-02 | Standard API, type and member names never change. | Name is in `protected-tokens/<language>` for the tested version. |
| P-03 | Runtime, file, CLI, protocol, schema, JSON/CSV key and entry-point names never change (default no). | Change only with a migration that moves producers, consumers, tests and docs together, proved by the oracle. |
| P-04 | A project-owned identifier is a candidate for a Spanish rename. | Needs an `identifier-map.jsonl` record with scope and test evidence. |
| P-05 | Comments are translated, line for line. | Same line count; code samples inside comments stay valid. |
| P-06 | A display string is translated only if no format, parser, fixture, column width or lesson depends on its bytes. | Classification recorded per string; otherwise keep and record why. |
| P-07 | `Meetings`, `Coding`, `Debugging`, `Learning` and any fixture value stay English by default. | A change needs an explicit decision in `loop/decisions-provisional.md`. |
| P-08 | Opaque fixtures and adversarial payloads never change. | Exception only with proof the bytes are not the lesson, a same-failure-mode replacement, and a test under the right engine. |
| P-09 | Anything else, or no safe proof, stays English. | A row in `translation/exception-register.jsonl` gives the reason. |
| P-10 | Spelling alone never decides a class. | The class is recorded with the role (type, element, string, noun). |
| P-11 | The English `LICENSE`, `.gitattributes`, `.github`, Gradle wrapper files, `sandbox/` and generated or binary files never localize. | The scope file marks them `never: true`; `loc_apply.py` refuses them. |

## B. Decision ladder (4.5.2), asked in this order

1. Syntax or standard API: keep. 2. External or public contract: keep. 3. Project-owned identifier: choose a short, idiomatic, collision-free Spanish name; check scope, built-in shadowing and case rules; record it. 4. Comment: translate line for line. 5. String: classify (display, protocol, SQL, regex, path, locale-sensitive, lesson literal) and translate only proven-safe display strings. 6. Fixture or payload: keep. 7. No safe proof: keep and write down why.

- L-01 A rename is refused when the program exploits its own spelling (parser, regex, stringification, column width, macro expansion, file-system case, reflection, non-obvious scope).
- L-02 Native Spanish never overrides correctness.

## C. Hard rules for any Part II change (4.5.3)

- H-01 Scoped files only: a file changes only if its family is `localizing` in the scope file, and only through `tools/loc_apply.py`, which edits mapped spans and fails closed. No `sed`, no global replace, no hand edit of a protected region. Until S2-003 the pre-commit hook refuses every protected change.
- H-02 Line-preserving: a change that adds or removes a line is refused unless the task also updates `translation/line-anchors.jsonl`. COBOL columns, APL layout and Make tabs treat width as semantic.
- H-03 Atomic family commits: one family per task; code, README, copied excerpts, diagrams, trace tables, `identifier-map.jsonl`, derived `identifiers.yaml` and `dnt.txt` rules, and the oracle report move in one commit. A rename whose documentation lags is a defect.
- H-04 Language-aware editing: use the compiler, LSP or AST rename where one exists; for COBOL, APL, Forth, shell, m4, Make, regex, `ed`/`ex`, Tcl and `find`/`tar` use token-level edits with that language's lexical rules and test at every evaluation phase.
- H-05 Runtime evidence or no change: a family that cannot be built and run in the sandbox container is not localized and is reported `NOT TESTED` with the reason. A report never says "verified" for a skipped family.
- H-06 Hostile examples run only in the sandbox container. The sandbox allowlist, `sandbox-gate.yml` and `scope-check.sh` are never weakened.
- H-07 Equivalence is differential (4.5.4): English and Spanish versions run in the same container; semantic records must be equal; the oracle must reject the planted mutant `total >= 40`.

## D. Stop and bubble-up rules (4.5.3 rule 7)

Stop the task, do not retry blindly, and mark it `blocked` with a small reproduced fixture and two alternatives in `loop/blockers.md`, then continue with an independent family, when:

- S-01 a rename would change a public contract;
- S-02 there are unexplained concurrent edits in the same files;
- S-03 a parser or build conflict makes two Spanish treatments impossible;
- S-04 an unavailable runtime tempts a "verified" claim (record `NOT TESTED` instead);
- S-05 the translator cannot substantiate a semantic mismatch;
- S-06 the sandbox would need a relaxation;
- S-07 the change touches bytes that are the lesson (regex, encoding, COBOL columns, security payloads).

Bubble-up means: write the blocker, name the family, and leave the family `frozen`. A later human decision may move it to `localizing`; the loop never does that on its own authority without the oracle proof of its own task.

## E. Status of the scope file

- C-01 Every family in `code-inventory.jsonl` has exactly one row in `localization-scope.yaml`, and the file counts match.
- C-02 At S1 every row is `frozen`. A row becomes `localizing` only inside its S5 task commit.
- C-03 A row marked `never: true` cannot become `localizing`.
- C-04 The tool S2-003 enforces C-01 to C-03; until then this document is the rule.

## F. Known limits at S1

The Docker self-test of the sandbox and the tool versions are still `NOT TESTED` (see `runtime-matrix.md`). By H-05 no family may become `localizing` until a Docker-capable session proves its runtime.
