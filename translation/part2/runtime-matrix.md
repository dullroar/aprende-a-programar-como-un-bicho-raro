# Part II runtime matrix (S0-003, PARTIAL)

Written by iteration 396. **Status of the evidence:** the session ran under `claude -p` dontAsk mode, which refused every `docker run` and `sandbox/selftest.sh` call (including a harmless `gforth --version` probe). So the sandbox self-test was **NOT RUN**, no tool version was read from a running container, and no entry was executed. Everything below comes from reading `src/*/Dockerfile`, `sandbox/container/build-bases.sh`, `sandbox/linux/Dockerfile`, `docker images` (listing only) and the entry files.

Labels:

- **PASS-capable (unproven):** a trusted runtime image exists locally and the entry has a `check.sh`. It becomes `PASS` only after the self-test passes and the oracle has run both English and Spanish versions. Until then no report may say "verified".
- **NOT TESTED:** no runtime here, or the runtime is not a Linux container. The family stays English (plan 4.5, rule 5) unless a later task changes that.

Remaining work for S0-003 (must be done by a session that may run Docker): run `sandbox/selftest.sh` and record its result here; read each tool version with `docker run --rm --network none --entrypoint <tool> <image> --version`; replace "version" cells that say "pinned in image, unread"; then promote or demote the labels. Do not run any entry on the host.

## Sandbox facts (read from the repository)

- Runner: `sandbox/run.sh` (build toolchain image `code-challenge-sandbox:local`) and `sandbox/container/run-image.sh src/<entry>` (per-entry image `cc-entry-<entry>:local` on a `cc-rt-*` base). No network, read-only root, no capabilities, user `nobody`, 256 processes, 2 GiB, 2 CPU, 15 min limit.
- Pinned in `sandbox/linux/Dockerfile`: PCRE2 10.49, GNU APL 2.0, Node 24.22.3 (also `runtime-node` in `sandbox/container/Dockerfile`). All other tools are Ubuntu 24.04 apt packages (base image pinned by digest `sha256:2198e4c6...`); their exact versions are unread.
- Local images present (`docker images`, 2026-11-22): all 18 `cc-rt-*` bases, `cc-build-go|java|rust`, `cc-test-overlay`, `code-challenge-sandbox`, and 30 `cc-entry-*` images (listed per row).

## Semantic record shape (plan 4.5.4)

Every record has: `cards` (ordered list of category index, hours, running total), `crossing_card` (the first card over 40, retained), `final_total`, `cards_kept`, `persisted` (database rows or file bytes written), `commit_status`, `exit_code`, `stdout`/`stderr` split, `encoding`/`separators` of any file written. Rows say which fields apply.

## Linux entries (`src/`)

| Entry | Language / runtime base | Image present | Version | Seed | Record shape | Label |
| --- | --- | --- | --- | --- | --- | --- |
| apl | GNU APL, `cc-rt-apl` | `cc-entry-apl-sample`, `-boundary` | APL 2.0 (pinned) | no, unseeded | cards, total, exit | PASS-capable (unproven) |
| apl-weird | GNU APL, `cc-rt-apl` | `cc-entry-apl-weird` | APL 2.0 (pinned) | no | cards, total, exit | PASS-capable (unproven) |
| awk | gawk, `cc-rt-awk` | `cc-entry-awk` | apt, unread | no | cards, total, persisted rows | PASS-capable (unproven) |
| awk-weird | gawk | `cc-entry-awk-weird` | apt, unread | no | same | PASS-capable (unproven) |
| cmake | CMake script, `cc-rt-cmake` | `cc-entry-cmake` | apt, unread | no | cards, total | PASS-capable (unproven) |
| cobol | GnuCOBOL (build in toolchain, run on `cc-rt-cobol`) | none (`cobol` itself) | apt, unread | no | cards, total, file bytes (columns) | NOT TESTED: no `cc-entry-cobol` image; only `cobol-weird` has one |
| cobol-weird | GnuCOBOL, `cc-rt-cobol` | `cc-entry-cobol-weird` | apt, unread | no | cards, total, file bytes | PASS-capable (unproven) |
| ed-weird | `ed`, `cc-rt-ed` | `cc-entry-ed-weird` | apt, unread | `check.sh` mentions a seed | cards, total, persisted | PASS-capable (unproven) |
| ex-weird | `nvi` (ex), `cc-rt-nvi` | `cc-entry-ex-weird` | apt, unread | no | cards, total | PASS-capable (unproven) |
| find-gnu | GNU find + sqlite, `cc-rt-sqlite` | `cc-entry-find-gnu` | apt, unread | no | cards, total, persisted rows | PASS-capable (unproven) |
| find-posix | POSIX find + sqlite | `cc-entry-find-posix` | apt, unread | no | same | PASS-capable (unproven) |
| forth | gforth, `cc-rt-gforth` | `cc-entry-forth` | apt, unread | no | cards, total | PASS-capable (unproven) |
| forth-weird | gforth | `cc-entry-forth-weird` | apt, unread | no | cards, total | PASS-capable (unproven) |
| haskell | GHC build, run on `cc-rt-haskell` | none | apt, unread | yes: `seed` derived from clock and pid; no fixed replay | cards, total | NOT TESTED: no `cc-entry-haskell` image |
| haskell-weird | GHC, `cc-rt-haskell` | `cc-entry-haskell-weird` | apt, unread | unread | cards, total | PASS-capable (unproven) |
| javascript | Node, `cc-rt-node` | `cc-entry-javascript` | Node 24.22.3 (pinned) | `SEED` env (Park-Miller in sibling entries) | cards, total, db rows, exit | PASS-capable (unproven) |
| javascript-events | Node | `cc-entry-javascript-events` | Node 24.22.3 | `SEED=42` replays a run | cards, total, db rows, exit | PASS-capable (unproven) |
| javascript-weird | Node | `cc-entry-javascript-weird` | Node 24.22.3 | unread | cards, total, db rows | PASS-capable (unproven) |
| lisp | SBCL, `cc-rt-sbcl` | `cc-entry-lisp` | apt, unread | no | cards, total | PASS-capable (unproven) |
| lisp-weird | SBCL | `cc-entry-lisp-weird` | apt, unread | no | cards, total | PASS-capable (unproven) |
| m4 | GNU m4, `cc-rt-m4` | `cc-entry-m4` | apt, unread | no | cards, total | PASS-capable (unproven) |
| make-gnu | GNU make, `cc-rt-make` | `cc-entry-make-gnu` | apt, unread | no | cards, total | PASS-capable (unproven) |
| regex-dotnet | .NET (build in toolchain, run `cc-rt-dotnet`) | `cc-entry-regex-dotnet` | dotnet-runtime-10.0 (apt) | no | match results, exit | PASS-capable (unproven) |
| regex-pcre2 | C + PCRE2 10.49, `cc-rt-pcre2` | none | PCRE2 10.49 (pinned) | no | match results, exit | NOT TESTED: no entry image |
| regex-pcre2grep | pcre2grep 10.49 (callouts), `cc-rt-sqlite` | `cc-entry-regex-pcre2grep` | 10.49 (pinned) | no | match results, exit | PASS-capable (unproven) |
| regex-perl | Perl, `cc-rt-sqlite` | none | apt, unread | `timecards.pl` mentions a seed | match results, exit | NOT TESTED: no entry image |
| regex-sed | sed, `cc-rt-sqlite` | `cc-entry-regex-sed` | apt, unread | no | match results, exit | PASS-capable (unproven) |
| tar-gnu | GNU tar + sh, `cc-rt-sqlite` | `cc-entry-tar-gnu` | apt, unread | yes: `--seed N` / `SEED`; same seed gives same bytes (`check.sh` asserts it) | cards, archive bytes, exit | PASS-capable (unproven) |
| tar-gnu-weird | GNU tar + sqlite | `cc-entry-tar-gnu-weird` | apt, unread | unread | cards, rows, exit | PASS-capable (unproven) |
| tcl | Tcl 8.6, `cc-rt-tcl` | `cc-entry-tcl` | apt, unread | no | cards, total | PASS-capable (unproven) |
| tcl-weird | Tcl 8.6 | `cc-entry-tcl-weird` | apt, unread | no | cards, total | PASS-capable (unproven) |

A fixed seed is not a cross-platform guarantee (plan 4.5.4); any trace under a seed will say so.

## Windows and GUI entries

| Entry | Runtime | Reason | Label |
| --- | --- | --- | --- |
| LinqChallenge1, LinqChallenge2, ModernChallenge1, xaml | .NET on Windows (WPF/XAML, EF Core) | Needs Windows Sandbox (`sandbox/windows/run.ps1`); this host is WSL2 Linux | NOT TESTED |
| PythonChallenge1 | Python/Tk, `cc-rt-pytk` base | GUI under Xvfb; no `cc-entry-` image and no `check.sh`; the sandbox README says GUI adaptations have no verification script | NOT TESTED |
| RustChallenge1 | Rust/GTK 4, `cc-build-rust` + `cc-rt-gtk` | Same: GUI, no entry image, no check | NOT TESTED |
| GoChallenge1 | Go web page, `cc-build-go` + `cc-rt-go` | No entry image; no `check.sh` | NOT TESTED |
| JavaChallenge1, KotlinChallenge1 | Swing, `cc-build-java` + `cc-rt-java` | GUI, no entry image, no check | NOT TESTED |

## Solutions (`lessons/solutions/`)

| Path | Runtime | Reason | Label |
| --- | --- | --- | --- |
| awk-port | gawk, `cc-rt-awk` (own `Dockerfile`, `check.sh`) | `cc-entry-awk-port` image exists | PASS-capable (unproven) |
| b7-linq | .NET/LINQ on Windows (`lq.csproj`) | no Linux image, no check | NOT TESTED |
| c2-forth-rule-check.sh | shell script around gforth | single file, no Dockerfile, no entry image; could run in a `cc-rt-gforth` container but nothing is wired | NOT TESTED |
| f-takewhile.hs | Haskell snippet | single file, no Dockerfile or entry image | NOT TESTED |

## Totals

- Linux entries: 32 rows; 28 PASS-capable (unproven), 4 NOT TESTED (cobol, haskell, regex-pcre2, regex-perl).
- Windows/GUI entries: 9, all NOT TESTED.
- Solutions: 4; 1 PASS-capable (unproven), 3 NOT TESTED.
- Sandbox self-test: **PASS** on 2026-11-23 (iteration 496). `bash sandbox/selftest.sh` ran and ended with `selftest: all good`: the hostile entry blocked every network, filesystem, privilege, secrets and resource probe, and the scope-check negative cases were rejected. Iterations 396 and 495 had it denied under dontAsk mode; the top-of-file "NOT RUN" note is historical. Tool versions are still unread, and no entry has been run through the oracle by this task, so the labels above stay "unproven".
