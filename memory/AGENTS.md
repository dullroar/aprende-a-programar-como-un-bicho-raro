# Memory index

<!-- IMMUTABLE HEADER: do not edit the text above the BEGIN marker. -->

This folder holds memories for agents. Humans read `GUIA-DEL-REPO.md` instead.

- One memory is one file. Many agents can write at the same time without a lock.
- Each file starts with front matter: `gist: "Read me when: <situation>"`.
- Edit the existing file for a topic. Do not add a second file for the same topic.
- **NEVER put PII, secrets, keys, tokens, passwords, personal paths or private host names in a memory.** Memory files are tracked by Git and can become public.
- Write in Simplified Technical English (ASD-STE100).
- This file is generated. Run `python3 scripts/build_indexes.py` after any change. Do not edit the list below by hand.

Read the list. Open only the files whose "Read me when" line matches your task.

<!-- BEGIN GENERATED INDEX -->

* [anchors-and-links.md](./anchors-and-links.md)
  Read me when: you translate or change a heading, a link fails (I16, I4, I2), or you apply a PO to a file.
* [build-and-pdf-checks.md](./build-and-pdf-checks.md)
  Read me when: you build the Spanish book, guides or PDF, run lessons/book scripts, or a PDF sentinel (PDF-010) or generated-file check fails.
* [code-localization-part2.md](./code-localization-part2.md)
  Read me when: you localize code comments or categories in Part II (src/ families), run the oracle, or edit a code PO or line-anchors.jsonl.
* [edition-wording-rules.md](./edition-wording-rules.md)
  Read me when: you translate card counts, hours ranges, sandbox wording, review items or edition identity, or you apply a review suggestion.
* [english-tree-import.md](./english-tree-import.md)
  Read me when: you import or compare the pinned English tree, or you need a command that touches the English clone.
* [glossary-and-style-lints.md](./glossary-and-style-lints.md)
  Read me when: verify --fast reports I3, I7, I11, I12, I24 or I25, or you add a glossary term, an identifier rule or a style rule.
* [inventory-and-verify-gates.md](./inventory-and-verify-gates.md)
  Read me when: you add a directory or file, localize a tooling file, or verify.py or inventory.py fails before a commit.
* [lock-code-and-pyc.md](./lock-code-and-pyc.md)
  Read me when: locked code, a CRLF file, a .pyc file or the lock check (I13 CHANGED) fails, or you set up a fresh clone.
* [mermaid-labels.md](./mermaid-labels.md)
  Read me when: you translate or change a Mermaid diagram, label or accDescr, or lint I21, I23 or the 8.4 pt label floor fails.
* [old-loop-queue-and-tools.md](./old-loop-queue-and-tools.md)
  Read me when: you edit a queue task, pick the next task, test the driver, or you need the project virtualenv and dependency rules of the old loop.
* [po-edits-and-waivers.md](./po-edits-and-waivers.md)
  Read me when: you must change a PO entry by hand, waive a lint finding (I3, I7, I9, I10, I12, I25), or regenerate an applied file from its PO.
* [review-jury-and-canaries.md](./review-jury-and-canaries.md)
  Read me when: you touch the review jury, packets, canaries, the recall test, or you commit anything under review/.
* [shell-denied-patterns.md](./shell-denied-patterns.md)
  Read me when: a Bash call is denied in a non-interactive agent session (dontAsk mode), or you plan a shell command that is not a single simple command.
* [source-issue-probes.md](./source-issue-probes.md)
  Read me when: you suspect a defect in the English book (Node ordering, PCRE2 JIT callouts, setImmediate) and must prove it before you log it.
* [study-guide-diagrams.md](./study-guide-diagrams.md)
  Read me when: you draft or fix a study guide, or its diagrams, shared-challenge paragraph or README copy do not match.
* [translate-py-workflow.md](./translate-py-workflow.md)
  Read me when: you run tools/translate.py on a file, it stops or leaves needs-revision entries, or you import drafts.

<!-- END GENERATED INDEX -->
