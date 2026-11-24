# F2-007-ex-weird batch report: card categories in src/ex-weird (decision 11)

Iteration 514. Verdict: **NOT TESTED / left English. The oracle fails in Spanish, so nothing was kept.**

## What was tried

C entries for the category words in `timecards.ex` (line 6), `timecards.sh` (grep pattern line 26, SQL CHECK list line 31) and `check.sh` (lines 19, 40, 48, 92, 93, 119, 120), plus the four comment spans that quote rows (`timecards.ex` L77, L80, L84; `timecards.sh` L4). `loc_apply.py` accepted them and the README prose and spans were regenerated. `tools/apply.py` was also extended to rewrite space-joined output rows (`Meetings 17 17`) in fences; that change was reverted along with the rest.

## Why it fails

- `python3 -I tools/oracle.py --entry src/ex-weird --english ~/english-source`: **FAIL** in Spanish ("stopped at 16, which is not strictly greater than 40"; "the first card over 40 was not kept as the last card"). Only one card was kept.
- No regex class around the card names exists in this family (unlike ed-weird), so the cause is not established. Likely cause (not verified; `run-image.sh` was denied in dontAsk mode, so the editor's output could not be inspected): the first card, `Reuniones`, is ASCII and the run dies on the second card, `Programación`, which suggests nvi in the image rejects the multibyte text under its locale.
- A C entry may change only category words; changing the image locale or the editor invocation is a code change outside the rules.

## State

- All edits reverted (`git checkout` of `src/ex-weird`, its code PO files, `tools/apply.py`, `tools/test_apply.py` and the two category lists). `lock_code --verify` ok.
- `translation/exception-register.jsonl`: EXC-589.
- README and `lessons/` text for this family keep the English category words.
- A later session that can run the image may diagnose the nvi failure; if it is a locale issue, an `ENV LANG=C.UTF-8` in the Dockerfile is not allowed (frozen code), so the family likely stays English.
