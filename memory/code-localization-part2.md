---
gist: "Read me when: you localize code comments or categories in Part II (src/ families), run the oracle, or edit a code PO or line-anchors.jsonl."
---

# Part II: code localization

## Oracle

- If `tools/oracle.py` FAILS on the English baseline too (`src/regex-pcre2`: card-sum mismatch), revert the edits and record NOT TESTED. Do not weaken the oracle inside an S5 family task.
- Run the oracle right after the first C-entry pass of a family. Revert at once on FAIL.
- Families that run an editor (ed-weird, ex-weird) fail the oracle once categories gain accents. `ex-weird` (nvi) fails even with no letter classes to widen. Do not retry it. Expect the same from sed-weird and any family that feeds Spanish words through nvi or vi. Check the editor, not only the regexes.
- Before you localize categories, grep the family's code for `[A-Za-z]` classes around card names. Accented words break them. C entries cannot change a regex. Leave the family English with an EXC row.
- Build-tooling families under `lessons/` (not `src/` entries) have no oracle runner. Leave them English with an exception row and a NOT TESTED report.
- The model reviewer misses a regex class that was narrowed from `A-Za-zÁÉÍÓÚáéíóúñ` back to `A-Za-z` (1 of 4 caught). Rely on the Spanish oracle. Rerun `recall_test.py --code FAMILIES` with a higher `--max-usd`, because old replies in `translation/work/recall` count against the budget.

## Entries and PO files

- `loc_apply` refuses format-like strings (class format-or-template). Only display-candidate strings can be translated.
- A COBOL comment line stays at 72 bytes or fewer. Accents count 2 bytes.
- A Forth line that has both a `( stack )` comment and a trailing `\ ` comment (for example `timecards.fs` 40 to 42) gives `loc_apply` two spans on one line, and it refuses them. Leave those comments English.
- A code line with a category word and a trailing comment is one C entry (category words only in the code part, the comment translated in the same entry). Never also give it an L entry. Overlapping edits are refused.
- To change a comment that S5 already applied: set that PO entry's msgid to the current Spanish file text, run `loc_apply --write`, then restore the English msgid. `loc_apply` refuses a msgid that matches neither side. To change an already localized comment by PO: edit the msgstr, copy the English file from `<english-clone>` over the Spanish one, then run `loc_apply.py PATH --write`. Then run `lock_code.py --write-localized` and `inventory.py` before verify.
- When a family's comments are localized, trim the `expect` of its `line-anchors.jsonl` records to the code part (`translation/work/reanchor.py`).
- After you widen classes or localize categories, run `verify --release --no-gates` at once. Seeded `line-anchors.jsonl` records on those lines (ed-weird 42, regex-perl 7) fail until their `expect` shows the new text. Fix them, then run `anchors.py --generate`.
- A tape of glued category words (`MeetingsCodingDebugging...`) is matched by `categories.WORD_RE` and `apply._WORD_RE` only as a run. A README code span with `[A-Za-z]` is widened by `apply.py`. Do not hand-edit it.
- For a family whose README fences copy archive records (`category=Coding`), `apply.py` `KEYVAL_RE` localizes them. After you edit `apply.py`, rerun `translation/work/regen_po.py REL` and grep the README for leftover English words.
- A README whose Mermaid labels or accDescr name the categories needs the file in both category-localized lists. Then run `regen_po.py REL`. I13 fails on a file that mixes English and Spanish category words.
- A negative fixture that edits the Spanish source cannot plant a bad code span. The PO restores code from the English. Plant it with `after=` on the finished file.
- Never name a scratch script `re.py`. It shadows the stdlib.
- In `lessons/` a build tool that uses `lessons/book` may need Spanish-only CSS or tooling in a separate file that `build.py` adds when the language is not `en`. A change to a layer file shared with English shows up as an EPUB hash diff in `tools/scratch_proof.py`.
- Re-run `python3 -I tools/scratch_proof.py` (about 5 minutes) after any change to the allowlisted tooling or the catalog. Start it in the background and poll its output file. Keep the metadata YAMLs out of the layer.
