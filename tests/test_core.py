import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from app.progress import Progress
from app.quiz import generate_quiz, get_translation, load_dictionary
from app.vocabulary import Vocabulary


class ProgressTests(unittest.TestCase):
    def test_level_curve_is_progressive_and_progress_is_bounded(self):
        progress = Progress()
        goals = [progress.xp_for_level(level) for level in range(1, 7)]
        self.assertEqual(goals[0], 0)
        self.assertEqual(goals, sorted(goals))
        progress.add_xp(200)
        state = progress.level_progress()
        self.assertGreaterEqual(state["percent"], 0)
        self.assertLessEqual(state["percent"], 100)

    def test_invalid_progress_json_does_not_crash(self):
        progress = Progress()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            path.write_text("not json", encoding="utf-8")
            progress.load(str(path))
        self.assertEqual(progress.xp, 0)
        self.assertEqual(progress.level, 1)


class VocabularyTests(unittest.TestCase):
    def test_correct_review_is_spaced_and_wrong_review_is_due_today(self):
        vocabulary = Vocabulary()
        vocabulary.add_word("light", "Genesis 1:3")
        self.assertEqual(vocabulary.words["light"]["next_review"], date.today().isoformat())

        vocabulary.record_review("light", correct=True)
        self.assertEqual(
            vocabulary.words["light"]["next_review"],
            (date.today() + timedelta(days=1)).isoformat(),
        )
        vocabulary.record_review("light", correct=False)
        self.assertEqual(vocabulary.words["light"]["next_review"], date.today().isoformat())
        self.assertEqual(vocabulary.words["light"]["incorrect_reviews"], 1)

    def test_old_json_is_loaded_with_new_fields(self):
        vocabulary = Vocabulary()
        vocabulary.from_dict({"light": {"origin": "Genesis 1:3", "reviews": 2}})
        self.assertEqual(vocabulary.words["light"]["reviews"], 2)
        self.assertIn("next_review", vocabulary.words["light"])


class QuizTests(unittest.TestCase):
    def test_missing_translation_does_not_fallback_to_portuguese(self):
        dictionary = {"light": {"pt": "luz"}}
        self.assertIsNone(get_translation("light", dictionary, native_lang="es"))

    def test_quiz_options_are_unique_and_have_no_placeholder(self):
        dictionary = load_dictionary()
        questions = generate_quiz(["light"], dictionary, native_lang="pt", limit=1)
        self.assertEqual(len(questions), 1)
        options = questions[0]["options"]
        self.assertEqual(len(options), len(set(options)))
        self.assertNotIn("???", options)

    def test_english_definitions_are_available_for_all_entries(self):
        dictionary = load_dictionary()
        self.assertTrue(dictionary)
        self.assertTrue(all(entry.get("en") for entry in dictionary.values()))


if __name__ == "__main__":
    unittest.main()
