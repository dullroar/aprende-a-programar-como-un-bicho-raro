---
gist: "Read me when: you translate card counts, hours ranges, sandbox wording, review items or edition identity, or you apply a review suggestion."
---

# Wording and decision rules of the edition

## Fact

- The shared challenge is 10 to 19 HOURS for each card (`de 10 a 19 horas por tarjeta`). Never write `tarjetas` for that range. Check every file that repeats the sentence. Write an I22 range as `de 10 a 19 horas (letras a)` with `hora` in the same sentence.
- Name the total explicitly at a card-count boundary. Name the actor explicitly when a Spanish relative clause can reverse who performs a technical action.
- Do not add guarantees that the English does not make (for example "no puede dañar nada"). Gloss sandbox once for each file, then say `entorno aislado`.
- Binding decisions live in `translation/review-decisions-2026-11-20.md`. Read its Parts B and C before you translate.
- Apply review items through the PO targets after you check the English. Record a disposition for each item. Log source-issue items in `translation/source-issues.md` only. The Spanish stays faithful to the English.
- Reject a review suggestion that contradicts a frozen glossary rendering (the five machine questions, `afirmación`, `decisión`), adds an inline code span (I2, I13), changes the bold count (I11), or alters the catalog sentence "La B es recursiva.". After you translate `docs/plan-de-estudios.md`, run `env PYTHONDONTWRITEBYTECODE=1 BOOK_LANG=es python3 -B lessons/plan-de-estudios/build.py --check`. Record the reason in the dispositions file.
- Edition identity (repository URL, branch, stems, title, es-419, UUIDs) lives in catalog block `identity.*`. After you change a Spanish value, recompute the three metadata identifiers with `repo_links.publication_uuid` in the same commit. If not, `test_repo_links.py` fails. Use the exact edition title from the catalog (`identity.book_title`).
- The README, guides and APL pages must match the patterns in catalog blocks `editorial.*` and `sentinels.*`. Run `env BOOK_LANG=es python3 lessons/book/test_editorial.py` after stage 4.
- A catalog number that differs by language (a word limit) is stored as quoted text and parsed in code. `catalog.py` requires integer values to be equal in `en.yaml` and `es.yaml`. Config keys may have capitals (`sentence_word_limit_N`). Read `loop/CONFIG.yaml` through `inventory.read_config`.
- Add every new locale key to BOTH `lessons/book/locale/en.yaml` and `es.yaml` in the same commit. Run `python3 -I lessons/book/locale/catalog.py --check es en` and `python3 -I tools/test_catalog.py`. Never name a package `locale`. Import `catalog.py` by putting its directory on `sys.path`.
- Locale phases: after you edit `lessons/book/locale/es.yaml`, run the OK locale phases 1 to 5. Edit only the acronym and phases blocks. Never change the Mermaid node IDs W E I R D.
- Audit by comparing a connective ("and", "plus") with the code that the sentence describes. Compare front-matter `teaches:` with the bold "Te enseña:" line in the same README. The deterministic gates catch neither.
- Before a refactor of a generator, hash its English output with `translation/work/cs_snapshot.py` (sha256 of `generate_all`). Require the same hash after.
- When you test a Spanish generator over English READMEs, call `diagrams.set_language("en")` after `cs.set_language("es")`. `generate_all` lists a block page only when its text differs.
- A generated block marker names its page by the English key. The entries' `lesson:` names it in the layout here. Compare through `cs.E()` (`cs.on_page`), never `==`.
- In `lessons/book/test_cs.py`, give a test its own README text in a scratch copy. Run `python3 -I tools/scratch_proof.py --tests` after every `lessons/book` test change.
- A test in `lessons/book` that reads a real file finds it with `catalog.checkout().path(english_path)`, never a literal path.
