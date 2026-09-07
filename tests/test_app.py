"""Headless UI checks; run with python -m unittest discover -s tests -v."""

import time
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


class ParagraphSheetTests(unittest.TestCase):
    def make_app(self):
        app = AppTest.from_file(str(APP), default_timeout=15).run()
        self.assertFalse(app.exception)
        return app

    def test_blank_start_and_word_target(self):
        app = self.make_app()
        self.assertEqual(app.text_area[0].value, "")
        self.assertEqual(app.metric[0].value, "30:00")
        app.text_area[0].input("word " * 400).run()
        self.assertIn("exactly 400", app.success[0].value)
        app.text_area[0].input("word " * 401).run()
        self.assertTrue(any("1 words over" in item.value for item in app.info))
        self.assertEqual(len(app.text_area[0].value.split()), 401)
        self.assertFalse(app.exception)

    def test_timer_rerun_expiry_and_reset_keep_draft(self):
        app = self.make_app()
        app.button(key="start").click().run()
        deadline = app.session_state["deadline"]
        self.assertAlmostEqual(deadline - time.monotonic(), 1800, delta=5)
        app.text_area[0].input("My paragraph stays here.").run()
        self.assertEqual(app.session_state["deadline"], deadline)
        app.session_state["deadline"] = time.monotonic() - 1
        app.run()
        self.assertEqual(app.metric[0].value, "00:00")
        self.assertIn("Time is up", app.warning[0].value)
        self.assertEqual(app.text_area[0].value, "My paragraph stays here.")
        app.button(key="reset_timer").click().run()
        self.assertEqual(app.metric[0].value, "30:00")
        self.assertIsNone(app.session_state["deadline"])
        self.assertEqual(app.text_area[0].value, "My paragraph stays here.")
        self.assertFalse(app.exception)

    def test_download_snapshot_clear_and_session_isolation(self):
        app = self.make_app()
        app.text_area[0].input("First paragraph.\n\nSecond paragraph — café.").run()
        app.button(key="prepare").click().run()
        self.assertEqual(app.session_state["download_copy"], app.text_area[0].value)
        app.text_area[0].input("New revision.").run()
        self.assertNotEqual(app.session_state["download_copy"], app.text_area[0].value)
        app.button(key="prepare").click().run()
        self.assertEqual(app.session_state["download_copy"], "New revision.")
        other = self.make_app()
        self.assertEqual(other.text_area[0].value, "")
        self.assertIsNone(other.session_state["deadline"])
        self.assertTrue(app.button(key="clear").disabled)
        app.checkbox(key="confirm_clear").check().run()
        app.button(key="clear").click().run()
        self.assertEqual(app.text_area[0].value, "")
        self.assertIsNone(app.session_state["download_copy"])
        self.assertFalse(app.checkbox(key="confirm_clear").value)
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
