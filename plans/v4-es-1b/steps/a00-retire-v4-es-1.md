---
id: a00-retire-v4-es-1
status: pending
depends_on: []
touches:
  - plans/v4-es-1/plan.md
  - plans/v4-es-1/goal.md
  - plans/v4-es-1/steps/**
  - plans/AGENTS.md
  - plans/v4-es-1b/steps/a00-retire-v4-es-1.md
lane: none
gate: test ! -e plans/v4-es-1/steps && grep -q 'Superseded by' plans/v4-es-1/plan.md && grep -q 'Superseded by' plans/v4-es-1/goal.md && test -f plans/v4-es-1/gatelib.py && python3 scripts/build_indexes.py --check && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
tier: light
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Mark plan v4-es-1 as superseded and keep its gate helper

Plan `v4-es-1b` replaces plan `v4-es-1`. No step of `v4-es-1` has started (all are `pending` on 2026-11-24). The gate helper `plans/v4-es-1/gatelib.py` stays: the gates of `v4-es-1b` use it.

## Change

- `plans/v4-es-1/plan.md`: after the front matter, add one paragraph: "**Superseded by `v4-es-1b` on <date>.** The steps of this plan were removed. `gatelib.py` stays as the shared gate helper of `v4-es-1b`. Do not run this plan." Change the `gist` line to start with "Superseded by v4-es-1b. Read me when: you need the history of".
- `plans/v4-es-1/goal.md`: add the same paragraph under the title.
- Remove `plans/v4-es-1/steps/` from Git (`git rm -r`). Steps u01 to u05, c01 to c05 and x01 are already copied to `plans/v4-es-1b/steps/`.
- Run `python3 scripts/build_indexes.py`.

## Do not change

- Files outside `touches`. The `gate`. `plans/v4-es-1/gatelib.py`, `plans/v4-es-1/loop.yaml`, `plans/v4-es-1/records/`.

## Done when

- `plans/v4-es-1/steps` does not exist, both banners are there, and the indexes are fresh.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
