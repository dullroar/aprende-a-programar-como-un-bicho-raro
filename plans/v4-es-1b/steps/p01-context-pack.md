---
id: p01-context-pack
status: pending
depends_on: [t08-pdf-review, j05-adjudication-apply]
touches:
  - review/fable/context.md
  - plans/v4-es-1b/steps/p01-context-pack.md
lane: none
gate: for h in 'What this is' 'Audience' 'What the edition tried to do' 'What was intentionally not translated' 'Already decided' 'Do not report' 'What to report' 'Output format'; do grep -q "^## $h" review/fable/context.md || exit 1; done && w=$(wc -w < review/fable/context.md) && test $w -ge 2000 -a $w -le 12000 && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write the English brief that Fable reads before the PDFs

Fable must understand what the project tried to do before it judges the PDFs. The brief is the cached prefix of every Fable request. Write it in English. Keep it under 12 000 words.

## Change

- `review/fable/context.md` with these sections, in this order:
  1. `## What this is`: the English book *Learn Programming the Weird Way!*, its companion study guides and the 16-week study plan; the Spanish edition and its label; the pinned English commit.
  2. `## Audience`: advanced programming students and working programmers in Latin America (`es-419`), informal `tú`, the author's direct and humorous voice. Readers from Spain and other regions must not be confused.
  3. `## What the edition tried to do`: from `translation/house-style.es.md`, `translation/decisions.md`, `review/EDITION-FACTS.md` and `TRADUCTORIO.md`: the translation rules, the glossary policy, the code-localization scope, the phase acronym, the humor policy (transcreate where the joke dies in Spanish), the safety rules (sandbox wording is never weaker than the English).
  4. `## What was intentionally not translated`: from the master prompt section of the same name (`translation/prompts/jury-master.md`).
  5. `## Already decided`: a short list of the rejected and `needs-source-issue` findings of `review/findings-*.jsonl`, grouped by pattern, so that Fable does not report them again. Never list canary data.
  6. `## Do not report`: the items of section 4 and section 5, and pure preferences of style that the house style allows.
  7. `## What to report`: anything a careful Spanish-speaking technical editor would mark in a printed book: meaning errors, unclear or awkward Spanish, inconsistent terms, layout defects (cut text, overflow, bad page breaks, unreadable figures or diagram labels, broken tables), wrong or dead cross-references, English left in reader-facing text, weaker safety wording, jokes that fall flat.
  8. `## Output format`: copy it from `translation/prompts/pdf-review.md`.
- Do not write a canary, a key, a path or a personal name.

## Do not change

- Files outside `touches`. The `gate`.

## Done when

- The eight headings are there, in order. The file has between 2 000 and 12 000 words.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
