import unittest

from atlasdb import AtlasDB


class TestJSONCompatibility(unittest.TestCase):
    """Test validation of JSON-compatible values."""

    def setUp(self):
        self.db = AtlasDB()

    def test_valid_basic_values(self):
        valid_values = [
            "sara",
            30,
            3.14,
            True,
            False,
            None,
        ]

        for value in valid_values:
            with self.subTest(value=value):
                self.assertTrue(self.db._is_json_compatible(value))

    def test_valid_lists_and_dictionaries(self):
        valid_values = [
            [],
            {},
            [1, 2, 3],
            {"name": "sett", "age": 30},
            {"user": {"years": 30, "months": 6}},
            {"languages": ["python", "go"]},
            {"mixed": [1, "hello", True, None, {"score": 3.14}]},
        ]

        for value in valid_values:
            with self.subTest(value=value):
                self.assertTrue(self.db._is_json_compatible(value))

    def test_invalid_values(self):
        invalid_values = [
            {"python", "go"},
            set(),
            (1, 2, 3),
            lambda x: x,
            float("inf"),
            float("-inf"),
            float("nan"),
            {1: "one", 2: "two"},
            {"nested": [{"invalid": {"python", "go"}}]},
        ]

        for value in invalid_values:
            with self.subTest(value=repr(value)):
                self.assertFalse(self.db._is_json_compatible(value))


class TestInsertDocument(unittest.TestCase):
    """Test insertion of documents into AtlasDB."""

    def setUp(self):
        self.db = AtlasDB()

    def test_insert_returns_an_id(self):
        document_id = self.db.insert_document(
            {"name": "sett", "age": 30}
        )

        self.assertIsInstance(document_id, str)
        self.assertTrue(document_id)

    def test_insert_stores_document(self):
        document_id = self.db.insert_document(
            {"name": "sett", "age": 30}
        )

        self.assertIn(document_id, self.db._documents)

    def test_stored_document_has_correct_values(self):
        document_id = self.db.insert_document(
            {"name": "sett", "age": 30}
        )

        stored = self.db._documents[document_id]

        self.assertEqual(stored["name"], "sett")
        self.assertEqual(stored["age"], 30)

    def test_stored_id_matches_dictionary_key(self):
        document_id = self.db.insert_document(
            {"name": "sett", "age": 30}
        )

        self.assertEqual(
            self.db._documents[document_id]["_id"],
            document_id,
        )

    def test_identical_documents_get_different_ids(self):
        first_id = self.db.insert_document(
            {"name": "sett", "age": 30}
        )
        second_id = self.db.insert_document(
            {"name": "sett", "age": 30}
        )

        self.assertNotEqual(first_id, second_id)
        self.assertEqual(len(self.db._documents), 2)

    def test_caller_cannot_supply_id(self):
        with self.assertRaises(ValueError):
            self.db.insert_document(
                {"_id": "my-id", "name": "sett"}
            )

        self.assertEqual(len(self.db._documents), 0)

    def test_invalid_document_is_rejected(self):
        with self.assertRaises(TypeError):
            self.db.insert_document(
                {"name": "sett", "skills": {"Python", "Go"}}
            )

        self.assertEqual(len(self.db._documents), 0)

    def test_inserting_does_not_modify_original_document(self):
        original = {
            "name": "sett",
            "metadata": {"level": "beginner"},
        }

        original_before = {
            "name": "sett",
            "metadata": {"level": "beginner"},
        }

        self.db.insert_document(original)

        self.assertEqual(original, original_before)
        self.assertNotIn("_id", original)


if __name__ == "__main__":
    unittest.main()
