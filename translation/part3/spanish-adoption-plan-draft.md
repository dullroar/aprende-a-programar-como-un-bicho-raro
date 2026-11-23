# Spanish adoption plan (DRAFT)

**Status: DRAFT.** Not final until the English upstream package is accepted by its maintainer and published. Nothing here has been run against an accepted revision. When the package is accepted, replace the pinned revision below, re-run the inventory (step A1), and mark this plan `final`.

## Pinned revision

- **Local upstream package base:** `48a4429c0a22b2aac628b256a50c07d1816bcb80` (the English SHA this edition already pins; see `translation/source.json`).
- **Package:** `translation/part3/upstream-package.patch`, applied on that base (H3-003, `translation/part3/upstream-package.md`).
- **Accepted upstream revision:** not yet known. The maintainer may squash, reword, or merge it on top of newer English commits. Record the real SHA in `translation/source.json` only after acceptance.

## Inventory: what the package changes, and what that touches in Spanish

The package is two files. It changes no prose of the book, no code, no diagram and no generated file.

| English change | Spanish prose | Code | Diagrams | Generated artifacts |
| --- | --- | --- | --- | --- |
| `CONTRIBUTING.md`: one sentence added after the intro ("Want to translate the book...") | Yes. Source unit changes, so the PO `msgid` for `CONTRIBUTING.md` changes. `translation/po/CONTRIBUTING.md.po` already carries a Spanish pointer to `TRADUCTORIO.md` inside the intro `msgstr` (H3-002); the English upstream puts it in a separate paragraph. | No | None (no Mermaid in the file; the Program Flow rule only cites it) | `CONTRIBUTING.md` (generated from the PO), and the PDF and EPUB if they embed it (check in A4) |
| `TRANSLATING.md` (new file, 101 lines) | Yes. A new English source file with no entry in `path-map.yaml`, `manifest.json` or `source-map.jsonl`. The Spanish repo already has its own `TRANSLATING.md` (English text, edition-owned) and `TRADUCTORIO.md` (Spanish counterpart); they must stay a reciprocal pair. | No | None (0 Mermaid fences in both guides) | None; not part of `lessons/book` |

Differences between the Spanish repo's `TRANSLATING.md` and the upstream one: the upstream copy replaces the "Working draft" banner with a two-line origin note, uses an absolute link for the Spanish guide, and its Ralph paragraph links the Spanish edition. The Spanish repo's copy still has the draft banner (line 3) and the relative link `TRADUCTORIO.md`.

Not affected: the 27 open source issues (`translation/source-issues.md`) are not in the package. If Jim approves any, each becomes its own English change and its own impact entry; see task A7.

## Decision to take before adoption (Jim)

Should `TRANSLATING.md` and `TRADUCTORIO.md` stay edition-owned (current state: written here, not translated from English) or become a translated pair of an upstream source? **Default if Jim does not answer:** keep them edition-owned; the upstream `TRANSLATING.md` is a copy of ours, so translating it back would be circular. Under that default A3 only reconciles the three wording differences, and `TRANSLATING.md` stays out of the PO flow. Reversal cost: low (add one path-map row and a PO file).

## Scoped tasks

Each task is one iteration of the loop. IDs are proposals; the queue generator assigns the real ones.

| ID | Scope | Verification | Targeted review |
| --- | --- | --- | --- |
| A1 | **Pin and diff.** Record the accepted revision. Run `python3 tools/impact.py --old <english checkout at 48a4429> --new <english checkout at accepted revision> --release <name>` and compare its map with the inventory table above. Any extra changed file means this plan is stale: stop and replan. | Impact map lists only `CONTRIBUTING.md` and `TRANSLATING.md` (plus anything the maintainer added, each named). `tools/lock_code.py` reports no frozen file changed. | None; the map is the evidence. |
| A2 | **CONTRIBUTING.md.** Update the PO: new English `msgid` for the changed intro, new `msgid` for the added sentence with a Spanish `msgstr` that points to `TRADUCTORIO.md`; remove the pointer from the intro `msgstr` so it is not said twice. Regenerate `CONTRIBUTING.md`. Update `source-map.jsonl` and the manifest hash. | `python3 tools/verify.py --fast`; PO and `CONTRIBUTING.md` regenerate with no diff on a second run; style lint passes (sentence length, tú imperative, `¿?` pairing). | One human or jury read of the single changed paragraph. |
| A3 | **Guide pair.** Per the decision above (default: edition-owned). Align the Spanish repo's `TRANSLATING.md` with the accepted upstream text: remove the draft banner only if Jim has signed off, use the same link forms the upstream chose for the Spanish edition, and keep `TRADUCTORIO.md` in step. | Diff of our `TRANSLATING.md` against the accepted upstream file shows only the intended differences (listed in the commit). `TRADUCTORIO.md` mirrors every section heading of `TRANSLATING.md`. | Bilingual read of both guides together (fidelity and readability), as in H3-001. |
| A4 | **Generated artifacts.** Check whether the PDFs and EPUBs embed `CONTRIBUTING.md`. If they do, rebuild; if not, record "not embedded". Run the double-build equality check. | `python3 tools/verify.py --release --no-gates` passes; two builds are byte-equal; `lessons/book/build.py --check` in the English checkout is unchanged. | None. |
| A5 | **Link and language-pair check.** After the Spanish repository is published and the accepted upstream revision exists: run `tools/link_audit.py`; check that `CONTRIBUTING.md` points to `TRADUCTORIO.md`, `TRADUCTORIO.md` points to `TRANSLATING.md` and back, and that the upstream `TRANSLATING.md` links to the published Spanish edition and its `TRADUCTORIO.md`. The upstream links in `upstream-package.md` resolve only after publication; check them then, not before. | Link audit has no new broken links (baseline: the 33 triaged in `translation/part2/link-audit.md`). Every contributor pointer resolves in both repos. | None. |
| A6 | **Pin bump.** Update `translation/source.json`, `loop/STATE.md` and the manifest to the accepted revision; tag a local release candidate only if A1 to A5 pass. Do not push. | `verify --release --no-gates` OK; frozen-file lock clean; `part2_inv` clean (no Part II file changes expected). | None. |
| A7 | **Approved source issues (only if Jim approves rows).** For each approved `SI-NNN`, a separate task: run the impact map for that English change, update the Spanish unit by the normal translate flow, and for code or generated content fix the source or generator, never the output by hand. | Per-change: impact map, `verify --fast`, and for code families the oracle in the sandbox. | One targeted review per changed paragraph; a Part II oracle run if code changes. |

Order: A1, then A2 to A4 in any order, then A5 (needs publication), then A6. A7 is independent and optional.

## What is out of scope

- Publishing, opening pull requests or contacting the English maintainer (Jim's step).
- Translating or changing the 27 open source issues without approval.
- Any change to frozen code, Part II localized families or the sandbox: the package touches none.

## Checks that already hold today (draft time)

- `CONTRIBUTING.md` (Spanish) links to `TRADUCTORIO.md`; `TRANSLATING.md` links to `TRADUCTORIO.md`; both files exist in the Spanish repo root.
- The English checkout at `/home/lehmer/english-source` has no `TRANSLATING.md`, as expected before the package is accepted.
- Not verified: the upstream-side links to the Spanish edition (the repository is not yet public) and the end-to-end adoption (no accepted revision exists).
