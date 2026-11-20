# Pilot: seeded-fault recall of the in-loop reviewer (task P3-007)

**Verdict: PASS.** recall on critical and major faults 100.0% (bar 95%), every 40-rule flip caught.

| Item | Value |
| --- | --- |
| Reviewer | anthropic/claude-sonnet-5-5 (alias: sonnet) (prompt translation/prompts/review.md, tools disabled, one unit per call) |
| Model ids seen | claude-haiku-5-5, claude-sonnet-5-5 |
| Translator | anthropic/claude-sonnet-5-5 (alias: sonnet) |
| Seed | 7 |
| Faults seeded | 50 (43 critical or major) |
| Clean controls | 10 |
| Spent | $1.87 |

A fault counts as caught only when a schema-valid finding with exact-substring excerpts points at the changed place. A finding elsewhere, or with an excerpt that is not an exact substring, earns nothing.

## Recall by category

| Category | Faults | Caught | Critical or major | Caught |
| --- | --- | --- | --- | --- |
| dnt-violation | 2 | 2 | 2 | 2 |
| modal-logic | 8 | 8 | 8 | 8 |
| number-operator | 17 | 17 | 17 | 17 |
| omission | 7 | 7 | 7 | 7 |
| phase-acronym | 1 | 1 | 1 | 1 |
| register | 7 | 7 | 0 | 0 |
| terminology | 8 | 8 | 8 | 8 |

## Recall by mutator

| Mutator | Severity | Faults | Caught | Caught at major or critical |
| --- | --- | --- | --- | --- |
| assurance_label | critical | 8 | 8 | 8 |
| category_in_span | major | 2 | 2 | 2 |
| drop_clause | major | 7 | 7 | 7 |
| flip_forty | critical | 10 | 10 | 10 |
| negation | major | 8 | 8 | 8 |
| phase_letter_after_fase | critical | 1 | 1 | 1 |
| register | minor | 7 | 7 | 4 |
| swap_number | major | 7 | 7 | 7 |

## 40-rule flips

10 seeded, 0 missed.

## Clean controls

1 of 10 clean units drew a critical or major finding with valid excerpts (0 findings rejected for non-exact excerpts across all controls).
- `docs/curriculum.md#s-d2ac8b96ed3a-0084`: major addition: The English is a bare list item. The Spanish adds an English term in italics and a definition that the source does not contain. The house rule says not to add c
- `docs/curriculum.md#s-d2ac8b96ed3a-0084`: major addition: This is another added explanation with no English source. It also changes the register of the cell by using a second-person 'pasas' inside a table of historical

These are leads, not proof of a translation fault: a human or the adjudicator decides.

## Every fault

| Fault | Mutator | Severity | Unit | Caught | Reported as | Valid findings | Rejected |
| --- | --- | --- | --- | --- | --- | --- | --- |
| X001 | flip_forty | critical | `lessons/study-guides/languages/apl.md#s-3894643a82b3-0038` | yes | critical | 2 | 0 |
| X002 | flip_forty | critical | `lessons/study-guides/languages/forth.md#s-8d9ba8475425-0025` | yes | critical | 2 | 0 |
| X003 | flip_forty | critical | `lessons/study-guides/languages/forth.md#s-78a7d749b03d-0019` | yes | critical | 1 | 0 |
| X004 | flip_forty | critical | `lessons/study-guides/languages/apl.md#s-ed850e2b415a-0025` | yes | critical | 1 | 0 |
| X005 | flip_forty | critical | `lessons/study-guides/languages/apl.md#s-78a7d749b03d-0019` | yes | critical | 1 | 0 |
| X006 | flip_forty | critical | `lessons/study-guides/languages/forth.md#s-0c4427c0641f-0039` | yes | critical | 1 | 0 |
| X007 | flip_forty | critical | `src/forth/README.md#s-7c642f8bed53-0029` | yes | critical | 1 | 0 |
| X008 | flip_forty | critical | `lessons/study-guides/languages/forth.md#s-f72ab19a33d0-0042` | yes | critical | 1 | 0 |
| X009 | flip_forty | critical | `lessons/study-guides/languages/apl.md#s-0f9b554db7c5-0031` | yes | critical | 1 | 0 |
| X010 | flip_forty | critical | `docs/curriculum.md#s-6870c3cb2599-0092` | yes | critical | 1 | 0 |
| X011 | assurance_label | critical | `lessons/study-guides/languages/forth.md#s-6f9fc49306b8-0088` | yes | critical | 1 | 0 |
| X012 | negation | major | `lessons/study-guides/languages/forth.md#s-5fb4c349d8a7-0093` | yes | critical | 1 | 0 |
| X013 | swap_number | major | `lessons/study-guides/languages/forth.md#s-0e9bc8ec49b3-0077` | yes | critical | 1 | 0 |
| X014 | drop_clause | major | `lessons/cs-source/concepts/recursion.md#s-b8d70c63c2a3-0020` | yes | major | 1 | 0 |
| X015 | register | minor | `docs/curriculum.md#s-102bca44e1e1-0098` | yes | major | 1 | 0 |
| X016 | category_in_span | major | `lessons/study-guides/languages/apl.md#s-52db87a4601c-0059` | yes | critical | 1 | 0 |
| X017 | phase_letter_after_fase | critical | `docs/curriculum.md#s-d2530eda36b4-0014` | yes | critical | 2 | 0 |
| X018 | assurance_label | critical | `lessons/study-guides/languages/forth.md#s-c0672c4055b1-0084` | yes | critical | 1 | 0 |
| X019 | negation | major | `docs/curriculum.md#s-30913e972320-0012` | yes | critical | 1 | 0 |
| X020 | swap_number | major | `lessons/study-guides/languages/forth.md#s-dfd7c04a7027-0055` | yes | major | 1 | 0 |
| X021 | drop_clause | major | `lessons/study-guides/languages/forth.md#s-c9166f841101-0009` | yes | critical | 2 | 0 |
| X022 | register | minor | `docs/curriculum.md#s-b33e3011f7e9-0040` | yes | minor | 2 | 0 |
| X023 | category_in_span | major | `lessons/study-guides/languages/forth.md#s-37aa0f571f08-0060` | yes | critical | 2 | 0 |
| X024 | assurance_label | critical | `lessons/study-guides/languages/forth.md#s-13bacec09830-0004` | yes | critical | 1 | 0 |
| X025 | negation | major | `docs/curriculum.md#s-d91cc2e2d067-0104` | yes | critical | 2 | 0 |
| X026 | swap_number | major | `docs/curriculum.md#s-a7957bb31779-0054` | yes | major | 1 | 0 |
| X027 | drop_clause | major | `docs/curriculum.md#s-6943ab1eb560-0099` | yes | major | 1 | 0 |
| X028 | register | minor | `docs/curriculum.md#s-964cdca1b9df-0115` | yes | major | 3 | 0 |
| X029 | assurance_label | critical | `lessons/study-guides/languages/apl.md#s-71e36732ab2c-0086` | yes | critical | 1 | 0 |
| X030 | negation | major | `lessons/study-guides/languages/apl.md#s-2f3844e27424-0112` | yes | critical | 1 | 0 |
| X031 | swap_number | major | `docs/curriculum.md#s-e9cb27e1c8ed-0065` | yes | critical | 1 | 0 |
| X032 | drop_clause | major | `lessons/study-guides/languages/apl.md#s-2839f2578dcd-0099` | yes | major | 1 | 0 |
| X033 | register | minor | `lessons/study-guides/languages/forth.md#s-cbf955794f8a-0005` | yes | major | 3 | 0 |
| X034 | assurance_label | critical | `lessons/study-guides/languages/apl.md#s-c297fffb9c5d-0089` | yes | critical | 1 | 0 |
| X035 | negation | major | `docs/curriculum.md#s-085950519a5d-0117` | yes | critical | 1 | 0 |
| X036 | swap_number | major | `lessons/study-guides/languages/forth.md#s-9c6bbaab1a01-0046` | yes | critical | 1 | 0 |
| X037 | drop_clause | major | `lessons/study-guides/languages/apl.md#s-698d7f9c4523-0020` | yes | critical | 1 | 0 |
| X038 | register | minor | `lessons/study-guides/languages/apl.md#s-94ef3318f472-0045` | yes | minor | 1 | 0 |
| X039 | assurance_label | critical | `lessons/study-guides/languages/apl.md#s-d916f0ce26d2-0087` | yes | critical | 1 | 0 |
| X040 | negation | major | `lessons/study-guides/languages/forth.md#s-074a2fd6c755-0091` | yes | critical | 1 | 0 |
| X041 | swap_number | major | `lessons/study-guides/languages/apl.md#s-4fd596217ea9-0053` | yes | critical | 2 | 0 |
| X042 | drop_clause | major | `lessons/study-guides/languages/apl.md#s-11c177a1fe56-0036` | yes | major | 2 | 0 |
| X043 | register | minor | `docs/curriculum.md#s-33130a988846-0097` | yes | minor | 2 | 0 |
| X044 | assurance_label | critical | `lessons/study-guides/languages/forth.md#s-84318d77a3df-0085` | yes | critical | 1 | 0 |
| X045 | negation | major | `lessons/study-guides/languages/apl.md#s-27fc60c30f78-0022` | yes | major | 4 | 0 |
| X046 | swap_number | major | `docs/curriculum.md#s-81a51588d581-0069` | yes | major | 1 | 0 |
| X047 | drop_clause | major | `lessons/study-guides/languages/apl.md#s-d7f2c1f9007c-0024` | yes | major | 2 | 0 |
| X048 | register | minor | `lessons/study-guides/languages/forth.md#s-405c1b857089-0064` | yes | major | 1 | 0 |
| X049 | assurance_label | critical | `docs/curriculum.md#s-b31fba58623f-0010` | yes | critical | 1 | 0 |
| X050 | negation | major | `docs/curriculum.md#s-d4b3ec471461-0075` | yes | critical | 1 | 0 |

## Limits of this test

- The playfulness fault (a joke replaced by a flat literal rendering) cannot be seeded mechanically and is not measured here; the Jury canaries and the humor register cover it.
- Categories with fewer than 3 faults (dnt-violation, phase-acronym) have too few cases to show recall; the pilot files hold few such spots. The Jury canaries measure them on the full book.
- The faults are mechanical swaps in one segment. Faults that need context from another file (terminology drift, cross-file links) are not measured.
- The reviewer and the translator are the same model tier; independence is carried by the manual Jury (plan 9.1).
