# Upstream package for the English repository (H3-003)

Prepared locally. Nothing was pushed, no pull request was opened, nobody was contacted. The English checkout at `~/english-source` was not touched (`git status` clean); the work was done in a scratch clone.

## Base revision

`48a4429c0a22b2aac628b256a50c07d1816bcb80` (the pinned English SHA). Scratch clone branch `translating-guide`, in the session scratchpad (`.../scratchpad/en-upstream`), not committed there. The complete change is the patch `translation/part3/upstream-package.patch` (apply with `git apply` at the base revision).

## Full set of changes

| File | Change |
| --- | --- |
| `TRANSLATING.md` (new) | The Spanish repo's `TRANSLATING.md` after the H3-001 review, with three edits: the "Working draft" banner replaced by a two-line origin note linking the Spanish edition; the `Versión en español` link made absolute (the relative `TRADUCTORIO.md` does not exist in the English repo); the Ralph paragraph links the Spanish edition and says `loop/` and `tools/` paths refer to that checkout. |
| `CONTRIBUTING.md` | One sentence added after the intro: translators read `TRANSLATING.md` first. |

No other file changed. Spanish-edition links point to `https://github.com/dullroar/aprende-a-programar-como-un-bicho-raro` (`.../blob/main/TRADUCTORIO.md`). **They resolve only after Jim publishes that repository**; check them then.

## English repository checks

Run in the scratch clone with the change applied:

- `python3 lessons/book/build.py --check`: pass (metadata ok, generated files up to date, internal links ok, 517 headings checked). Note: 79 diagrams were not rendered (Mermaid CLI not installed); that gate is unchanged by this package.
- `pytest` on `test_document_links.py`, `test_repo_links.py`, `test_repo_identity.py`: 20 passed.
- The build rewrote the tracked file `lessons/book/__pycache__/build.cpython-312.pyc`; it was restored. (English repo quirk: a `.pyc` is tracked. Not part of the package; could be reported.)
- Not run: Docker `sandbox/` gates (Docker denied), and `scope-check.sh`, which governs entry pull requests, not this one.

## Sign-off still owed

The draft banner was removed because the H3-001 review is done, but the guide's own banner said to finalize after "maintainer sign-off". That sign-off has not happened. Jim should read the guide before it goes upstream.

## Upstream improvements found during translation

`translation/source-issues.md` holds 27 rows (SI-001 to SI-027), all `open`: **none is approved for upstream**, so none was applied to the English files in this package. They are candidates only. The evidence for each is in its row; the strongest are the ones verified by running software:

| ID | Evidence |
| --- | --- |
| SI-019 | Node v24.15.0 prints `nextTick` then `promise` under `--input-type=commonjs`, the reverse under `--input-type=module`. |
| SI-021 | PCRE2 manuals `pcre2callout(3)` and `pcre2jit(3)` document JIT callouts. |
| SI-022 | Node v24.15.0 run: `setImmediate` runs before an earlier queued 1 ms timer from an `fs.readFile` callback. |
| SI-023 | Folding `[2,3]` with `+` and seed 1 gives 6; seeding both halves gives 7. |

Reasoning-only (arithmetic or reading the specification and code): SI-001, 002, 009 to 018, 020, 024 to 026. Wording and formatting: SI-003 to SI-008, SI-027.

Suggested next step for Jim: mark the rows to send as `approved`, then a later task can add them to the package as separate commits.
