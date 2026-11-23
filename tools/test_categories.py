import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as c  # noqa: E402


class Categories(unittest.TestCase):
    def test_the_two_forms_pair_up(self):
        self.assertEqual(len(c.EN), 4)
        self.assertEqual(c.to_english("Depuración"), "Debugging")
        self.assertEqual(c.to_english("Coding"), "Coding")

    def test_one_form_only_is_clean(self):
        self.assertEqual(c.forms_used("`Meetings` y `Coding 12 12`"), {"en"})
        self.assertEqual(c.forms_used("```text\nReuniones\t12\t12\n```"), {"es"})
        self.assertFalse(c.mixed("`Reuniones` y `Programación`"))

    def test_word_after_tally_marks_counts_and_other_glue_does_not(self):
        self.assertEqual(c.forms_used("`Coding 15 xxxMeetings 12|xx`"), {"en"})
        self.assertTrue(c.mixed("`Programación 15 xxxMeetings 12|xx`"))
        self.assertEqual(c.forms_used("`yMeetings`"), set())

    def test_glued_tape_counts_each_word_and_a_stray_digit_does_not(self):
        self.assertEqual(c.forms_used("`MeetingsCodingDebuggingLearningMeetings247250`"), {"en"})
        self.assertTrue(c.mixed("`MeetingsProgramaciónDebuggingLearning247`"))
        self.assertEqual(c.forms_used("`Meetings2`"), set())
        self.assertEqual(c.forms_used("`xMeetings247`"), set())

    def test_mix_is_a_fault(self):
        self.assertTrue(c.mixed("`Meetings` y `Programación`"))
        self.assertTrue(c.mixed("`Meetings` y\n\n```text\nProgramación\t12\t12\n```"))

    def test_plain_prose_is_not_checked(self):
        self.assertFalse(c.mixed("# Depuración\n\nEl aprendizaje y `Meetings`."))
        self.assertEqual(c.wrong_spellings("La Reunión de hoy"), [])

    def test_wrong_spellings_in_code_are_found(self):
        self.assertEqual(c.wrong_spellings("`Reunión` y `Programacion 3 3`"), ["Reunión", "Programacion"])
        self.assertEqual(c.wrong_spellings("`Reuniones`"), [])


if __name__ == "__main__":
    unittest.main()
