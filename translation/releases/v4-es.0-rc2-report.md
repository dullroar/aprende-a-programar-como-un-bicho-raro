# Release report: v4-es.0-rc2 (Part II, code localization; local, nothing published)

Written in iteration 489 (task S8-005), 2026-11-23, for branch `loop/es-v4` at commit `82200c85815544a2f4fe716314ebb6554f98ea20` (S8-004). It extends the rc1 report (`v4-es.0-rc1-report.md`). The report records what was run in earlier iterations (S8-001 to S8-004, quoted from their gate files) and what was not. No command was re-run for this report, except the hash listing below.

## Identity

| Item | Value |
| --- | --- |
| Edition label | v4-es.0-rc2 (no tag created by this task) |
| Pinned English source | `48a4429c0a22b2aac628b256a50c07d1816bcb80` |
| Frozen-file lock | `translation/locked-code.sha256`, 230 entries (all still checked) |
| Localized-file lock | `translation/localized-code.sha256`, 109 rows |
| Scope file | `translation/localization-scope.yaml` (53 families) |

## Tool versions

Python 3.12.3, git 2.43.0, pandoc 3.1.3 (rc1 report), mermaid-cli 12.2.0 (S6-003), WSL2 Ubuntu 24.04 (Linux 6.6.87.2). Docker and language toolchains: denied in the unattended `dontAsk` mode (see `translation/part2/runtime-matrix.md`).

## Commands and exit codes

| Command | Exit | Result | Source |
| --- | --- | --- | --- |
| `python3 tools/verify.py --release` | 0 | OK, 86 checks, 386.6 s; double build identical hashes | S8-001, `translation/part2/s8-gate.md` |
| `python3 tools/scratch_proof.py` | 0 | PASS (pre-1 86 s, pre-2 49 s, post-1 49 s, post-2 48 s) | S8-001 |
| `python3 tools/link_audit.py --json ... --md translation/part2/link-audit.md` | non-zero (verdict FAIL) | broken 33, unverified 578, not executed 0 | S8-001 |
| `python3 -I tools/part2_inv.py --check` | 0 | 0 findings | S7-003, S8-002 |
| `python3 tools/lock_code.py --verify` | 0 | 230 frozen files match; localized lock ok | S5-999, S7-003, S8-002 |
| `python3 -I tools/verify.py --release --no-gates` | 0 | all checks pass | S5-999, S7-003 |
| `python3 tools/next_task.py` | 2 | normal ("task printed") | this task |

## Tests: RUN / NOT RUN

| Area | Status | Notes |
| --- | --- | --- |
| Release verify (86 checks, A and B builds) | RUN | S8-001 |
| Scratch proof (Spanish layer built from scratch, twice) | RUN, PASS | S8-001 |
| Part II invariants I28 to I31 (`part2_inv`) | RUN, 0 findings | S7-003, S8-002 |
| Frozen and localized locks | RUN, ok | S8-002 |
| Negative fixtures (`part2_negative`, 16 of 16 fail for the stated reason; lock fixtures 68 of 68) | RUN | S2-006, S5-999. Rows 10, 12, 14 deferred |
| Tool tests: `loc_map` (24), `loc_apply` (31), `oracle` (16), `link_audit` (24), `impact` (22), jury code packet tests | RUN, passing when each task was committed | S2-S3, S8-003, S8-004 |
| Mermaid render of 79 diagrams; 191 fences match English skeletons | RUN | S6-003 |
| Oracle equivalence (containers) for 30 localized families | RUN, PASS | per family report, see matrix |
| Oracle equivalence for 15 families left English | NOT RUN (NOT TESTED) | docker denied, no entry image, network needed, or no runner |
| Docker self-test (`tools/oracle.py` real container run) | NOT RUN | owed to a Docker-capable session (S0-003, S2-004) |
| Language toolchain version capture | NOT RUN | `runtime-matrix.md` is static |
| Link audit over built HTML, PDF and EPUB (`--html/--pdf/--epub`) | NOT RUN | S8-001 |
| Independent human or cross-vendor review of code comments | NOT RUN | S7-001 was a same-family native-voice sample |
| Full read of all localized comments by a human | NOT RUN | jury packets (S8-004) are ready for it |
| Known English-layout failures in `lessons/book/test_editorial.py` and `test_cs.py` | NOT RUN in the release gate | pre-existing, see rc1 caveat 3 |

## Oracle matrix (45 S5 families)

Policy: comments only; categories and display strings kept English where proof was not available (EXC-542 to EXC-586). Reports are in `translation/part2/reports/S5-fam-<name>.md`.

**Localized, oracle PASS (30):** apl, apl-weird, awk, awk-weird, cmake, cobol, cobol-weird, ed-weird, ex-weird, find-gnu, find-posix, forth, forth-weird, haskell, haskell-weird, javascript, javascript-events, javascript-weird, lisp, lisp-weird, m4, make-gnu, PythonChallenge1, regex-pcre2grep, regex-perl, regex-sed, tar-gnu, tar-gnu-weird, tcl, tcl-weird.

**Left English, NOT TESTED (15):**

| Family | Reason |
| --- | --- |
| lessons-book-diagrams, lessons-solutions, lessons-solutions-awk-port, lessons-solutions-b7-linq, lessons-tools | build tooling or solutions; no oracle runner |
| gochallenge1, javachallenge1, kotlinchallenge1, rustchallenge1 | image build needs network |
| modernchallenge1, linqchallenge1, linqchallenge2, xaml | no entry image (C#/WPF) |
| regex-dotnet, regex-pcre2 | oracle fails on the unmodified English baseline |

Earlier pilot reports: `S4-001-forth.md`, `S4-002-csharp.md`, `S4-003-cobol.md`. Audits: `translation/reviews/S5-audit-1.md` to `S5-audit-6.md` (no violations). S7-002 later changed 36 "desafío" to "reto" in 27 `src/` files via PO and `loc_apply`, oracle PASS x18.

## Link audit

Counts from S8-001 (`translation/part2/link-audit.md`): **broken 33, unverified 578, not executed 0**, verdict FAIL for Markdown source. Triage (S8-002): 29 in `lessons/cs-source/**` (resolve after generation, same layout as English), 1 plan note, 1 `loop/SIGNS.md` literal, 2 fixture links (intentional), 2 pinned-English-repository URLs (intentional). No review-fix tasks were opened. The link audit over built output was not executed.

## Hashes

Root artifacts (sha256, checked in this iteration; identical to rc1, so Part II comment changes do not alter the book PDFs or EPUBs):

| File | sha256 |
| --- | --- |
| aprende-a-programar-como-un-bicho-raro.pdf | e75ba85f673e3694a71f9a75b857046b93227fe9de5d478bea98a846626fae8c |
| aprende-a-programar-como-un-bicho-raro.epub | 7aca2f147014dc4aee0f28dee35af276b7a42d80fe72cc515cc10baa0d5ca2d3 |
| aprende-a-programar-como-un-bicho-raro-guias-de-estudio.pdf | 3302ee321c459e19d9605b83dde17c38d38ee8dfd805fd4f51e399c3c3be11b0 |
| aprende-a-programar-como-un-bicho-raro-guias-de-estudio.epub | 077d2038862f6684e6067fbe5d8ceea812803dc2f224ddc03f2ac719a0602693 |
| plan-de-estudios.pdf | cf89659cfea279ff1d80354a58dd6a9a9ea47b95c4e15ee14aace570fb9ccb43 |
| plan-de-estudios.epub | c6346cde3323dc2d5d811fa12fccae8ba7d625c1f494edd0156ac6ecb9307f52 |

Caveat: the release gate (S8-001) built the six publications twice with equal hashes, but this report did not compare those builds with the checked-in files. Treat the equality with rc1 as "same bytes on disk as in the rc1 report", not as a rebuild proof.

## Counts

Exception register 586 rows; humor register 175 rows; 212 PO catalogs; 31 files in `translation/reviews/`; source issues 26 plus SI-027 (token audit).

## Reviewer and model IDs

- Translator and in-loop reviewer: `claude-sonnet-5-5`. Not an independent vendor review (`cross_vendor_review: false`).
- Codex `gpt-6.1-terra` (standard tier, medium effort) produced translation drafts and one review-fix iteration; `claude-haiku-5-5` (light tier) did regen and gate work. See `python3 tools/model_report.py`; Part II `localize-code` iterations (50) ran on `claude-sonnet-5-5`.
- Spend ledger: `loop/ledger/usage.jsonl`.

## Caveats

1. Oracle PASS covers 30 of 45 families; 15 remain English and NOT TESTED, so Part II is partial by design.
2. Only comments were localized. No identifier, category or display string was renamed (identifier ledger empty; decision 11 forms apply only where a family was localized and proven).
3. F6 of the S7 native-voice findings is deferred (decisions-provisional.md).
4. Docker self-test and the built-output link audit are owed to a session that can run them.
5. The rc1 caveats (no full human read, open "Vivo" question, deferred tree-fence translation) still apply.
6. Nothing is pushed or tagged.
