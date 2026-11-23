# G1-003 batch report: card categories in src/ex-weird (decision 11, follow-up)

Iteration 538. Verdict: **NOT TESTED / left English. Oracle FAIL in Spanish again; edits reverted. EXC-589 updated.**

## Accent-safe regexes

The family has no `[A-Za-z]` class around card names. The only letter class is the `a-z` in the `check.sh` line 32 lint (it matches ex command letters in the program text), and accents do not touch it. So there was nothing for the G1-001 widening to do here; the ed-weird cause does not apply.

## What was tried

C entries for the category words in `timecards.ex` (C6), `timecards.sh` (C26, C31) and `check.sh` (C19, C40, C48, C92, C93, C119, C120), and the Spanish comment spans that quote rows (`timecards.ex` L77, L80, L84; `timecards.sh` L4), applied from the English baseline with `loc_apply.py`. All were accepted.

## Why it fails

- `python3 -I tools/oracle.py --entry src/ex-weird --english /home/lehmer/english-source --seed 3`: **FAIL**. English keeps 3 cards (13, 23, 42); Spanish keeps 1 (18) and stops. The default seed shows the same shape.
- The first card is `Reuniones` (ASCII) and works. The run dies on the next card, which starts with an accented word. The program text has no category-dependent pattern (`.*`, `[0-9]` and mark arithmetic only), so the cause is `nvi` in the image rejecting or garbling non-ASCII input under its locale.
- Fixing that needs a locale setting in the frozen `Dockerfile` or `timecards.sh`, which a C entry (category words only) may not do. `run-image.sh` is denied in dontAsk mode, so the editor output could not be inspected.

## State

- `git checkout` of `src/ex-weird` and its code PO files; the Spanish comments from S5 remain. README and lessons keep the English category words for this family.
- Not run on the host (hard rule 1).
