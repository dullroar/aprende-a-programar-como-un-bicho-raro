import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import token_audit as ta  # noqa: E402

TOK = {"List": ["java"], "list": ["python"], "print": ["python"], "return": ["python"],
       "for": ["python"], "os": ["python"], "path": ["python"], "my_var": ["x"], "if": ["python"]}


def run(text):
    return ta.audit_text(text, TOK, "t.md")


def names(text):
    return [f["token"] for f in run(text)]


class Positive(unittest.TestCase):
    def test_literal_list_type(self):
        self.assertEqual(names("El tipo List<String> guarda textos."), ["List"])

    def test_call_shape(self):
        self.assertEqual(names("Llama a print(x) para ver el valor."), ["print"])

    def test_member_access(self):
        self.assertIn("os", names("Usa os.path para unir rutas."))

    def test_sql_keywords_together(self):
        self.assertEqual(names("Escribe SELECT nombre FROM usuarios para leer."), ["FROM", "SELECT"][::-1])

    def test_mixed_code_and_prose(self):
        f = run("Usa `print(x)` y luego print(y) otra vez.")
        self.assertEqual([(x["token"], x["col"]) for x in f], [("print", 24)])

    def test_identifier_shape(self):
        self.assertEqual(names("La variable my_var cambia."), ["my_var"])

    def test_finding_row_has_path_line_reason(self):
        f = run("a\nUsa List[int] aquí.")[0]
        self.assertEqual((f["path"], f["line"], f["reason"]), ("t.md", 2, "call-or-type-shape"))


class FalsePositiveGuards(unittest.TestCase):
    def test_spanish_lista_quiet(self):
        self.assertEqual(run("Haz una lista de compras y devuelve el resultado."), [])

    def test_ordinary_words_quiet(self):
        self.assertEqual(run("Para cada caso, if you like, return later; for me, list it."), [])

    def test_single_sql_word_quiet(self):
        self.assertEqual(run("Elige SELECT del menú."), [])

    def test_quoted_keyword_joke_quiet(self):
        self.assertEqual(run('Él dijo "return" y se fue; luego "for" también.'), [])

    def test_inline_code_quiet(self):
        self.assertEqual(run("Usa `List<String>` y `SELECT a FROM b`."), [])

    def test_fenced_block_quiet(self):
        self.assertEqual(run("```sql\nSELECT a FROM b\nprint(x)\n```\n"), [])

    def test_tilde_fence_and_nesting(self):
        self.assertEqual(run("````\n```\nprint(x)\n```\nprint(y)\n````\n"), [])

    def test_link_and_url_quiet(self):
        self.assertEqual(run("Mira [la guía](docs/print(x).md) y https://x.org/os.path/list(1)."), [])

    def test_macros_quiet(self):
        self.assertEqual(run("Mira {{print(x)}} y [[List<T>]]."), [])

    def test_front_matter_and_comment_quiet(self):
        self.assertEqual(run("---\ntitle: print(x)\n---\n<!-- print(x) -->\nhola\n"), [])

    def test_indented_code_quiet(self):
        self.assertEqual(run("Texto\n\n    print(x)\n"), [])

    def test_comparison_not_a_type(self):
        self.assertEqual(run("Si a < b entonces for < 3."), [])

    def test_table_not_wrapped_or_flagged_without_evidence(self):
        self.assertEqual(run("| lista | return |\n|---|---|\n| for | if |\n"), [])


class Output(unittest.TestCase):
    def test_render_is_stable_jsonl(self):
        out = ta.render(run("Usa List<T>."))
        self.assertTrue(out.endswith("\n"))
        self.assertEqual(out, ta.render(run("Usa List<T>.")))

    def test_audit_never_edits(self):
        text = "Usa List<T>."
        run(text)
        self.assertEqual(text, "Usa List<T>.")

    def test_registry_loads_real_tokens(self):
        reg = ta.load_registry()
        self.assertIn("python", sum(reg.values(), []))

    def test_missing_registry_is_empty(self):
        self.assertEqual(ta.load_registry("/nonexistent/x.jsonl"), {})


if __name__ == "__main__":
    unittest.main()
