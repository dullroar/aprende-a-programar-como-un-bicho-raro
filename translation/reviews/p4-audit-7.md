# P4-audit-7 (iteration 340, 2026-11-22)

In a fresh Claude iteration, five segments were sampled from the eight completed translation tasks in the audit's queue record (language lessons csharp-linq-xaml through tcl, the curriculum front matter, the lessons README). The answers-key tasks have no PO file yet, so they are not in the pool. The draw is weighted by English length. The pool contains 708 nonempty PO entries across 14 files. To reproduce it, sort the files by English path and the entries within each file by position, then draw with `random.Random(339).choices(range(len(pool)), weights=len_of_msgid)` until five distinct entries are chosen.

| English file and source line | Segment | Review |
| --- | --- | --- |
| `lessons/languages/editors.md:5` | `s-d54f537d20c2-0002` | Pass. Link and destination placeholder intact; "recorrido avanzado de lectura" is faithful. |
| `lessons/languages/tcl.md:76` | `s-69deafebd9dc-0034` | Pass. The three code placeholders are in the right slots, "una por tarjeta" is kept. Observation: "drawn once" becomes "extraerse una sola vez", which reads as a fair idiom for pulling a value out once. |
| `lessons/languages/m4.md:68` | `s-0965352f2739-0031` | Pass. Bold lead kept, the list of colliding characters is complete, and the "L21" link and code slots are right. |
| `lessons/languages/javascript.md:78` | `s-ae24aa0271c0-0044` | Pass. The three items of the README contents are kept in order; "sin cuerpo" is faithful for "bodiless". |
| `lessons/languages/javascript.md:141` | `s-51d8d9310707-0083` | **Finding F008 (minor).** The English is one sentence with three joined conditions for a legitimate use. The Spanish cuts it into three sentences, and the second one, "El remitente no debe conocer a los destinatarios", now reads as a rule imposed on the reader instead of a condition. The third one turns "should not block" into "no debe bloquear". |
