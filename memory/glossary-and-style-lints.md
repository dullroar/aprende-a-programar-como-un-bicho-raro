---
gist: "Read me when: verify --fast reports I3, I7, I11, I12, I24 or I25, or you add a glossary term, an identifier rule or a style rule."
---

# Glossary and style lints

## Fact

- I7 checks each segment. A segment must hold the glossary form of each term that its English holds. Example: "hours" needs `horas`, and "running total" needs `total acumulado`. Reword to include the approved term. Do not waive when a reword works.
- I3 counts digit tokens for each segment. Reuse a digit only as often as the English does. Keep "1,000" as written. Spell out "ten", "three" and "zero" where the English does.
- I12 limits a sentence to 28 or 29 words. Placeholders count. Split long sentences at the draft stage.
- I24 allows one `(*term*)` gloss for each file.
- I25 fires on ", y" after a list and on a comma before "y". Use ";" or a new sentence. It also fires on NBSP before `%`. A percent sign in a protected URL: confirm that the percent-encoded destination stayed byte-identical, then record a segment exception.
- I11 enforces only catalog keys named `lead_in_*` for fixed bold lead-ins. Bold count must match the English.

## Add a glossary term

- Add the glossary row first. Run `python3 -I tools/glossary_check.py`.
- A term whose English word is ambiguous (port, in place, dispatcher, input line) gets a parenthesized `en`, so I7 builds no regex for it. Put the other sense in `note`.
- Check the English files for a second sense before you add a `banned` entry.
- A new plain-word term makes I7 flag every already-translated file that lacks it. Run `verify --fast --files` on them first.
- After you edit `translation/glossary.es.yaml`, run the glossary check. Quote YAML scalars that contain `: `. Never write `banned: [a, "b" text]`.
- Fixed renderings: "exit code" is `estado de salida` (`código de salida` is banned). Expect an I7 waiver for the word "code". "callback" is `función de devolución de llamada`. "string" is `cadena de texto`. English "build" as a verb needs an I7 waiver. I7 wants `compilación` for the noun "build". Keep English "branch" and "loop" as `rama` and `bucle`, and "thread" as `hilo`. When the glossary wants `forzar` or `costo`, use that literal lemma ("antes de forzar", "ningún costo").
- English "entry" next to "registers" or "log" makes I7 ban `registro`. Waive that segment.
- A table of "Compara los diseños ordinarios y los raros" uses that glossary heading even for one pair.

## Identifier and style rules

- Add a name that must stay literal (label, accDescr, table cell) as a rule in `translation/identifiers.yaml` with an English-context regex.
- Add a new absolute-claim phrase to `translation/style-lint.yaml`.
- Run `python3 -I tools/test_prose_lint.py` and `python3 -I tools/negative.py` after. Item 13 fixtures use the second control pair EN_B/ES_B. Write a non-breaking space as `chr(0xA0)` or `<NB>`.
- Style checks (I7, I9, I10, I12, I14) read the MASKED target with placeholders stripped, never the restored text. Check literal phase letters on the PO msgstr BEFORE macro expansion (`check_segment raw=`). Check ambiguity on the expanded text. A colliding letter after "fase" needs its name (`phase_lint.py`).
- A waiver is only an exception-register row that names the segment and the invariant.
- After you touch `tools/invariants.py`, run `python3 -I tools/test_invariants.py`.
- Add a plan 10.2 negative case as a Fixture in `tools/negative.py`. Mutate the finished file with `after=` when the target is a protected token, because the PO layer restores code from the English mask. A fixture that returns no problems means the gate is disarmed. Fix the gate, never the fixture.
