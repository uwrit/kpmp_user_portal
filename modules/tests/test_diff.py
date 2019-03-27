import unittest
from modules.app.diff import has_model_changed


class TestDiffModelChanged(unittest.TestCase):
    def test_has_changed(self):
        old = {
            "first_name": "John",
            "last_name": "Doe"
        }
        new = {
            "first_name": "John",
            "last_name": "Smith"
        }
        self.assertTrue(has_model_changed(old, new))

    def test_has_not_changed(self):
        old = {
            "first_name": "John",
            "last_name": "Doe",
            "last_changed_on": None
        }
        new = {
            "first_name": "John",
            "last_name": "Doe",
            "last_changed_on": ""
        }
        self.assertFalse(has_model_changed(old, new))


if __name__ == "__main__":
    unittest.main()
