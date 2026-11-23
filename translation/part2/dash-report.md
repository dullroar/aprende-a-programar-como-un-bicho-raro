# Dash report (F2-002)

Scope: every spaced hyphen (` - `) used as a dash in Spanish `msgstr` text of `translation/po/**` (prose and code comments). Edits were made in the PO files and applied with `tools/apply.py`. Pairs became `—texto—` (RAE style); single dashes became ` — `.

Search: `(?<=\S) - (?=\S)` plus a check for a hyphen standing alone across a line break; the second search found nothing.

## Replaced (9 dashes, 6 entries, 3 files)

| File | Count | Form |
|---|---|---|
| README.md | 2 | pair, "lenguaje —sus iteradores … compilación— antes" |
| README.md | 2 | pair, "del lenguaje —LINQ … callouts— que" |
| README.md | 1 | single, table cell "en ⟦CODE⟧ — una prueba lo exige" |
| src/LinqChallenge1/README.md | 1 | single, "ventana de terminal WPF — todo dentro" |
| src/LinqChallenge2/README.md | 1 | single, "⟦CODE⟧ — exactamente la forma" |
| src/LinqChallenge2/README.md | 2 | pair, "deliberada —"el pensamiento retorcido es buen pensamiento"— y no" |

## Skipped (9 cases)

| File | Case | Reason |
|---|---|---|
| code/src/cobol-weird/timecards.cob.po | 3 × `* - ` | list bullet inside a comment block, not a dash |
| code/src/cobol/timecards.cob.po | `MOD(día - 1, 7)` | arithmetic minus in code text |
| code/src/m4/timecards.m4.po | 2 × `2^31 - 1` | arithmetic minus |
| lessons/answers-key.md.po | `65 - 46 = 19` | arithmetic minus |
| src/LinqChallenge1/README.md.po | `⟦SEP⟧ - ⟦SEP⟧` | table separator |
| src/javascript/README.md.po | `⟦DNT⟧ - no real time system …` | part of a verbatim window title, program output |

English `msgid` text is untouched, and so are code, inline code, URLs, paths, flags and number ranges. No code file changed, so the lock and the oracle are unaffected.
