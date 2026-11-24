# Adoption of the pinned controls

Library: `deterministic-controls` `v0.1.1`, commit `0323de273a158608f7280867e12994141bccd1e6`.
State: advisory. The `controls` job of `.github/workflows/context.yml` reports. It is not a required check.
The `secret-guard` job is blocking. It is not part of this adoption.

## Receipt

Output of `adopt receipt` (base revision `10ab20febcb69c5c068d23c96354d3723a173f62`):

- Profile: `ci`. Enforcement state: `advisory`.
- Enabled checks: `context.index-freshness`, `plans.graph`, `plans.schema`, `repo.forbidden-artifacts`, `security.secrets`. All five passed.
- Files added: `scripts/check_context.py`, `scripts/controls-requirements.txt`, `controls.toml`.
- File changed: `.github/workflows/context.yml`.
- Commands kept: `scripts/build_indexes.py`, `scripts/ctx_common.py`, `scripts/verify_fast.sh`, CI job `secret-guard`.

## Scope decisions

- `context.index-freshness`: enabled. It is the same check as `build_indexes.py --check`.
- `plans.schema` and `plans.graph`: enabled. They are cheap. They check the step files of each plan.
- `repo.forbidden-artifacts`: enabled. It lists the paths that must stay untracked:
  `review/canaries.key.json`, `review/packets/**`, `review/repo-bundle.zip`, `review/units.index.jsonl`, `loop/driver.out*`.
  The library has default patterns too.
- `security.secrets`: enabled. The library marks it as mandatory.
- `markdown.local-links`: not enabled. Its scope includes `docs/`, which is the book content with thousands of files.
  It reports `README.md`, which links to a PDF that is a build output and is not in Git. The check has no parameter to exclude a path.
  The book has its own link audit (`tools/link_audit.py`).
- `security.personal-data`: not enabled. Its scope includes `docs/` and `plans/`.
  It reports a personal path in `plans/adopt-ralph/steps/t02-layout.md`. That file is outside the `touches` of this step.
  The check has no parameter to exclude a path. The owner can fix that line and enable the check.
  The secret guard still blocks secrets in every commit.

## Changes to the generated files

- `scripts/check_context.py` uses the library if Python can import it (the pinned library on `PYTHONPATH`).
  Without it, the shim builds a cached environment from the pin, as `adopt apply` wrote it. It exits `2` if the library cannot run.
- The `controls` job uses the same checkout action pin as the `secret-guard` job. `adopt apply` wrote a different SHA.
  The job installs the library from `scripts/controls-requirements.txt`, runs the check and runs `tools/verify.py --fast`.
- `scripts/controls-requirements.txt` has a `Run me when:` line already.

## Where the tools did not fit

- `adopt apply` put the secret guard steps in the new job. The `secret-guard` job has them already, so they were removed from `controls`.
- `markdown.local-links` and `security.personal-data` cannot be scoped. See above.
- The old check names `check_links.py` and `scan_secrets.py` in the shim map to library checks. A disabled check prints no line.

## Secret guard history scan

`python3 scripts/secret_guard.py --history`: 0 findings, 0 allowed. 108 binary files were not scanned (PDF, EPUB, PNG, JAR, PYC). Date: 2026-11-23.
The planning audit found none. The count is the same.

## Rollback

1. Delete `controls.toml`.
2. Delete `scripts/check_context.py`.
3. Delete the `controls` job from `.github/workflows/context.yml`. Keep the `secret-guard` job.
4. Delete `scripts/controls-requirements.txt` and run `python3 scripts/build_indexes.py`.
5. Delete `tools/test_controls.py`.
