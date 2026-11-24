---
id: t08-pdf-review
status: pending
depends_on: [a03-batch-review-kind]
touches:
  - tools/pdf_review.py
  - tools/test_pdf_review.py
  - tools/fixtures/pdf-review/**
  - translation/prompts/pdf-review.md
  - plans/v4-es-1b/steps/t08-pdf-review.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_pdf_review.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write pdf_review.py: Fable tickets by page chunk and an ingest that finds file and line

Fable reads the built PDFs and changes nothing. Feedback must give the PDF page and the source file and line. The tool never trusts a line number from the model: it finds the quote in the sources.

## Change

- `translation/prompts/pdf-review.md`: the Fable prompt. It starts with the brief `review/fable/context.md` (step p01; use a fixture in tests). Output: JSONL findings, each with `pdf` (file name), `page` (printed page index from 1), `quote` (exact text from the page, 5 to 40 words), `severity` (`critical|major|minor|suggestion`), `category` (`accuracy|clarity|style|layout|figure|link|consistency|safety|playfulness|other`), `problem` (English), `suggestion` (Spanish or English, never applied). A header line with `juror_model`. Do not report what the brief lists under "Do not report".
- `tools/pdf_review.py`:
  - `chunks --pdf FILE --pages N`: split into chunks of N pages (default 20) with `pdfseparate` and `pdfunite`, or a pure-Python fallback if those tools are missing. Write the text of each page with `pdftotext -layout` next to it.
  - `rows --pdfs FILE... --brief FILE --out-dir D`: one row for each chunk: the brief in the cached prefix, the chunk as a PDF document block, the page numbers in the tail. Extend `batch.py --kind review` input with an optional `document_file` only if a03 has no way to send a PDF block (check the Messages API reference for the PDF block and its limits, and write the URL in the docstring).
  - `probe-rows --pdf FILE --chunks 2 --brief FILE --out-dir D`: two chunks for the W0 probe: the first chunk, and the chunk with the most pages that name arbitrary code execution, weird machines or exploits (search the page text). Record which pages they are.
  - `tickets` as in `tools/jury_requests.py`.
  - `route --findings FILE --out review/fable/routing-<date>.md` and `route-merge` / `route-check`: write one line `<id> route: fix|reject|editors` for each finding (default: verified `critical` and `major` → `fix`, unless the category is `playfulness` or the finding names a guarantee, the 40-rule, safety or the acronym → `editors`; everything else → `editors`). Jim edits the lines in step p05. `route-merge` sets `status: accepted` (fix), `rejected` or `editors` in the findings. `route-check` fails if a line has no valid route or a `reject` has no reason after ` - `.
  - `ingest --results DIR --pdfs FILE... --out-dir review/fable/`: for each finding: check that `quote` is in the page text (whitespace-normalized); find it in the Spanish sources (`docs/`, `lessons/`, `src/**/README.md` and the other generated Markdown) and in `translation/po/*.po`; write `source_file`, `source_line`, `po_file`, `po_line` (all hits when there are several). A finding whose quote is not on its page, or that has no source hit, goes to the "Unverified" section. Write `review/fable/report-<date>.md` (English, sorted by severity, then file and line) and `review/fable/findings-<date>.jsonl`.
- Tests: a quote not on its page; a quote with two source hits; a chunk split of a 3-page fixture PDF; a refusal reply is recorded as failed for that chunk.

## Do not change

- Files outside `touches`. The `gate`. Any built PDF.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
