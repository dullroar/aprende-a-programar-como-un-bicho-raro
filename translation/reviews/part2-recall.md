# Part II seeded-fault recall of the model reviewer (task G1-008)

**Run command:** `python3 -I tools/recall_test.py --run --code ed-weird,regex-pcre2grep,regex-perl,regex-sed,tar-gnu --faults 24 --controls 4 --max-usd 5 --out translation/reviews/part2-recall.md` (seed 7, reviewer sonnet).

**Headline numbers:** recall 21/24 = 87.5% (bar 95%: FAIL); false alarms 1 of 4 clean controls (25%).

**What was run:** the real model reviewer on 28 localized code chunks (60 lines each, only chunks that differ from the English) of the five G1 families (ed-weird, regex-pcre2grep, regex-perl, regex-sed, tar-gnu). Five mutators: code-semantics, protected-token, build-ci, code_category (respelled card word) and code_unwiden (the widened accent class put back to `A-Za-z`). Each unit got one fault. ex-weird (left English) and tcl/other families were not run.

**What was not run:** no 40-rule flip (code chunks hold none), no prose units, no Docker oracle (the oracle is a separate proof), no larger sample (24 faults, 4 controls: wide error bars; 4 controls cannot size the false-alarm rate).

**Finding:** all 3 misses are `code_unwiden` (1 of 4 caught): the reviewer does not notice that a regex class lost its accented letters, which breaks Spanish category matching. The other four classes are 20/20. The deterministic detector that covers this class is the oracle (accents in Spanish run); the model reviewer must not be relied on for it. The one flagged control (`src/ed-weird/timecards.sh`) is a cross-file remark on the localized CHECK constraint, a lead, not a fault. `translation/prompts/review.md` was not changed. The recall tool gained `--code` (tools/recall_test.py); the report body below is the tool's output, whose generic title and "Pilot" wording are not Part II specific.

---

# Pilot: seeded-fault recall of the in-loop reviewer (task P3-007)

**Verdict: FAIL.** recall on critical and major faults 87.5% is below the bar 95%; no 40-rule flip was seeded

| Item | Value |
| --- | --- |
| Reviewer | anthropic/claude-sonnet-5-5 (alias: sonnet) (prompt translation/prompts/review.md, tools disabled, one unit per call) |
| Model ids seen | claude-haiku-5-5, claude-sonnet-5-5 |
| Translator | anthropic/claude-sonnet-5-5 (alias: sonnet) |
| Seed | 7 |
| Faults seeded | 24 (24 critical or major) |
| Clean controls | 4 |
| Spent | $3.53 |

A fault counts as caught only when a schema-valid finding with exact-substring excerpts points at the changed place. A finding elsewhere, or with an excerpt that is not an exact substring, earns nothing.

## Recall by category

| Category | Faults | Caught | Critical or major | Caught |
| --- | --- | --- | --- | --- |
| build-ci | 5 | 5 | 5 | 5 |
| code-semantics | 9 | 6 | 9 | 6 |
| dnt-violation | 5 | 5 | 5 | 5 |
| protected-token | 5 | 5 | 5 | 5 |

## Recall by mutator

| Mutator | Severity | Faults | Caught | Caught at major or critical |
| --- | --- | --- | --- | --- |
| build_ci | major | 5 | 5 | 5 |
| code_category | major | 5 | 5 | 5 |
| code_semantics | critical | 5 | 5 | 5 |
| code_unwiden | critical | 4 | 1 | 1 |
| protected_token | critical | 5 | 5 | 5 |

## 40-rule flips

0 seeded, 0 missed.

## Clean controls

1 of 4 clean units drew a critical or major finding with valid excerpts (0 findings rejected for non-exact excerpts across all controls).
- `src/ed-weird/timecards.sh#c-e0d0c922a11c-0001`: major cross-file: The CHECK constraint accepts only the localized category names. The script never produces those values. It imports whatever rows timecards.ed prints into the st

These are leads, not proof of a translation fault: a human or the adjudicator decides.

## Every fault

| Fault | Mutator | Severity | Unit | Caught | Reported as | Valid findings | Rejected |
| --- | --- | --- | --- | --- | --- | --- | --- |
| X001 | code_semantics | critical | `src/tar-gnu/check.sh#c-8a09c47e4d3c-0003` | yes | critical | 2 | 0 |
| X002 | protected_token | critical | `src/regex-pcre2grep/timecards.sh#c-88741728ee38-0001` | yes | critical | 3 | 0 |
| X003 | build_ci | major | `src/regex-perl/Dockerfile#c-30f9e9b85d5b-0001` | yes | critical | 2 | 0 |
| X004 | code_category | major | `src/regex-pcre2grep/check.sh#c-a4dd689890c6-0002` | yes | critical | 1 | 0 |
| X005 | code_unwiden | critical | `src/regex-sed/timecards.sed#c-6906baaee486-0001` | yes | critical | 1 | 0 |
| X006 | code_semantics | critical | `src/tar-gnu/interpret.sh#c-7b5d94fbe10e-0001` | yes | critical | 2 | 0 |
| X007 | protected_token | critical | `src/regex-sed/check.sh#c-2ff9d5b9782e-0002` | yes | critical | 1 | 0 |
| X008 | build_ci | major | `src/regex-pcre2grep/Dockerfile#c-78c7eb004960-0001` | yes | critical | 2 | 0 |
| X009 | code_category | major | `src/tar-gnu/build-archive.sh#c-f7cce09ce714-0001` | yes | major | 1 | 0 |
| X010 | code_unwiden | critical | `src/tar-gnu/check.sh#c-8a09c47e4d3c-0002` | **NO** | - | 1 | 0 |
| X011 | code_semantics | critical | `src/tar-gnu/dispatch.sh#c-11ff421c03de-0002` | yes | critical | 1 | 0 |
| X012 | protected_token | critical | `src/tar-gnu/timecards.sh#c-14cd940b83e0-0001` | yes | critical | 2 | 0 |
| X013 | build_ci | major | `src/regex-sed/check.sh#c-2ff9d5b9782e-0001` | yes | critical | 3 | 0 |
| X014 | code_category | major | `src/tar-gnu/inspect.sh#c-a21817f665a1-0001` | yes | critical | 1 | 0 |
| X015 | code_unwiden | critical | `src/regex-sed/timecards.sed#c-6906baaee486-0002` | **NO** | - | 0 | 0 |
| X016 | code_semantics | critical | `src/regex-pcre2grep/check.sh#c-a4dd689890c6-0001` | yes | critical | 4 | 0 |
| X017 | protected_token | critical | `src/tar-gnu/dispatch.sh#c-11ff421c03de-0001` | yes | critical | 2 | 0 |
| X018 | build_ci | major | `src/ed-weird/Dockerfile#c-a5ed270d4310-0001` | yes | critical | 2 | 0 |
| X019 | code_category | major | `src/ed-weird/timecards.ed#c-554cb2dcd343-0001` | yes | major | 3 | 0 |
| X020 | code_unwiden | critical | `src/ed-weird/check.sh#c-7f339e164272-0002` | **NO** | - | 0 | 0 |
| X021 | code_semantics | critical | `src/regex-sed/timecards.sh#c-c8766749bf58-0001` | yes | critical | 1 | 0 |
| X022 | protected_token | critical | `src/ed-weird/check.sh#c-7f339e164272-0001` | yes | critical | 2 | 0 |
| X023 | build_ci | major | `src/tar-gnu/Dockerfile#c-8ecfdf159aa3-0001` | yes | critical | 1 | 0 |
| X024 | code_category | major | `src/tar-gnu/check.sh#c-8a09c47e4d3c-0001` | yes | critical | 2 | 0 |

## Limits of this test

- The playfulness fault (a joke replaced by a flat literal rendering) cannot be seeded mechanically and is not measured here; the Jury canaries and the humor register cover it.
- Categories with fewer than 3 faults (none) have too few cases to show recall; the pilot files hold few such spots. The Jury canaries measure them on the full book.
- The faults are mechanical swaps in one segment. Faults that need context from another file (terminology drift, cross-file links) are not measured.
- The reviewer and the translator are the same model tier; independence is carried by the manual Jury (plan 9.1).
