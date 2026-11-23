# Accent-safe letter classes (task G1-001)

Decision 11 localizes the four card categories (`Reuniones`, `Programación`, `Depuración`,
`Aprendizaje`). Several families (ed, ex, regex-perl, regex-sed, regex-pcre2grep, tar-gnu) read
a category with an ASCII class such as `[A-Za-z]+`, which cannot match `ó`. Until now this left them
English (EXC-588 to EXC-593).

## The edit class

`tools/loc_apply.py` accepts, inside a `C<line>` PO entry, one more change besides category words and
`PIC X(n)` widths: an ASCII letter class `A-Za-z` inside brackets may become
`A-Za-zÁÉÍÓÚáéíóúñ` (the extension sits directly after `z`, spelled exactly so).

Rules, all enforced and tested (`tools/test_loc_apply.py`, tests `test_widen_*`):

- Every other byte of the line must stay equal, apart from category words and `PIC X(n)` widths.
- Every `A-Za-z` in the English line must be widened, or none (all or nothing).
- The English line must hold an `A-Za-z` bracket class; a `[0-9]` class or a loose `.` is refused.
- A partial extension (`ÁÉÍ`) or a foreign letter (`ü`) is refused.
- Narrowing a class already widened is refused; re-applying a widened line is a no-op.
- The oracle (`tools/oracle.py`) must still prove English and Spanish behavior equal; the tool only
  makes the edit possible, it does not replace the proof.
