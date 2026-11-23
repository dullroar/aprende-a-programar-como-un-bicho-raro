# S3 gate (iteration 415, task S3-003)

Scope: the link audit (`tools/link_audit.py`, S3-001) and the line-anchor check (S3-002), run on the rc1 checkout.

## Evidence

- `python3 tools/link_audit.py --json translation/reports/link-audit.json --md translation/reports/link-audit.md` wrote both reports. Verdict: **FAIL**. 33 broken, 578 unverified, 0 not executed.
- `tools/test_link_audit.py`: 33 passed.

## Broken links (33), listed honestly, not fixed here

- 29 in `lessons/cs-source/` (chapters and concepts): links keyed to Spanish file names (`../guias-de-estudio/conceptos/...`, `../objetivos.md`, `../introduccion.md#...`, `../../SANDBOX-SETUP.md`, `../../src/*/README.md`, `../lenguajes/regex.md`) that do not resolve from the cs-source location in this checkout, plus two Spanish fragments missing from chapter 05. These files feed the generator for `lessons/cs/*.md`; fix the source or generator, then regenerate (rule 4). Left for a repair task; not edited in a gate.
- 2 in `SYNTHESIZED-TRANSLATION-PLAN-es-bicho-raro.md:1262` (TRANSLATING.md, TRADUCTORIO.md): planning document, names files not yet created.
- 1 in `loop/SIGNS.md:119` (`DEST`): a literal placeholder in a rule's prose, not a link.
- 2 wrong-repository links to the English repo (`review/inbox/chatgpt-editorial-2026-11-20.md:7`, `translation/house-style.es.md:3`): deliberate pins to the English source commit.
- Test fixtures (`tests/fixtures/mixed.md`, 2) are planted-broken inputs for tests.

## Unverified (578)

External URLs: the loop makes no network calls (hard rule 2), so each is listed with reason "external URL: no network calls are made". Unmapped line-anchor links are also unverified. EPUBCheck was not executed.

## Result

Gate recorded as **PASS WITH DEFECTS LISTED**: accept (reports exist, tests pass) met; the 29 cs-source defects need a repair task before release.
