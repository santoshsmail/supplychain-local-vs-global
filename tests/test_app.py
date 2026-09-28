import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class AppTests(unittest.TestCase):
    def test_initial_views_and_results(self):
        app = AppTest.from_file(APP).run()
        self.assertFalse(app.exception)
        self.assertIn("Local vs global", app.title[0].value)
        self.assertTrue(any("6.5" in m.value for m in app.metric))

    def test_changing_allocation_and_zero_disruption(self):
        app = AppTest.from_file(APP).run()
        app.segmented_control[0].set_value("Who decides").run()
        app.slider(key="decision_weight").set_value(1.0).run()
        self.assertFalse(app.exception)
        app.segmented_control[0].set_value("Buy ahead").run()
        app.slider(key="disruption").set_value(0).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("both buy distant" in c.value.lower() for c in app.caption))

    def test_notebook_requires_observation_and_exports_note(self):
        app = AppTest.from_file(APP).run()
        app.button(key="add_note").click().run()
        self.assertEqual(len(app.session_state["notes"]), 0)
        app.text_area(key="observation").set_value("A loses units").run()
        app.text_input(key="evidence").set_value("Allocation records").run()
        app.button(key="add_note").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["notes"][0]["evidence_to_seek"], "Allocation records")
        self.assertEqual(len(app.get("download_button")), 1)


if __name__ == "__main__":
    unittest.main()
