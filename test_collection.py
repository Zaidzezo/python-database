
import unittest

from atlasdb import AtlasDB


class TestJSONCompatibility(unittest.TestCase):
    """Test validation of JSON-compatible values."""

    def setUp(self):
        self.db = AtlasDB()
        self.collection = self.db.collection("test_collection")

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
                self.assertTrue(
                    self.collection._is_json_compatible(value)
                )

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
                self.assertTrue(
                    self.collection._is_json_compatible(value)
                )

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
                self.assertFalse(
                    self.collection._is_json_compatible(value)
                )


class TestInsertDocument(unittest.TestCase):
    """Test insertion of documents into a Collection."""

    def setUp(self):
        self.db = AtlasDB()
        self.collection = self.db.collection("test_collection")

    def test_insert_returns_an_id(self):
        document_id = self.collection.insert_document(
            {"name": "sett", "age": 30}
        )

        self.assertIsInstance(document_id, str)
        self.assertTrue(document_id)

    def test_insert_stores_document(self):
        document_id = self.collection.insert_document(
            {"name": "sett", "age": 30}
        )

        self.assertIn(document_id, self.collection._documents)

    def test_stored_document_has_correct_values(self):
        document_id = self.collection.insert_document(
            {"name": "sett", "age": 30}
        )

        stored = self.collection._documents[document_id]

        self.assertEqual(stored["name"], "sett")
        self.assertEqual(stored["age"], 30)

    def test_stored_id_matches_dictionary_key(self):
        document_id = self.collection.insert_document(
            {"name": "sett", "age": 30}
        )

        self.assertEqual(
            self.collection._documents[document_id]["_id"],
            document_id,
        )

    def test_identical_documents_get_different_ids(self):
        first_id = self.collection.insert_document(
            {"name": "sett", "age": 30}
        )
        second_id = self.collection.insert_document(
            {"name": "sett", "age": 30}
        )

        self.assertNotEqual(first_id, second_id)
        self.assertEqual(len(self.collection._documents), 2)

    def test_caller_cannot_supply_id(self):
        with self.assertRaises(ValueError):
            self.collection.insert_document(
                {"_id": "my-id", "name": "sett"}
            )

        self.assertEqual(len(self.collection._documents), 0)

    def test_invalid_document_is_rejected(self):
        with self.assertRaises(TypeError):
            self.collection.insert_document(
                {"name": "sett", "skills": {"Python", "Go"}}
            )

        self.assertEqual(len(self.collection._documents), 0)

    def test_inserting_does_not_modify_original_document(self):
        original = {
            "name": "sett",
            "metadata": {"level": "beginner"},
        }

        original_before = {
            "name": "sett",
            "metadata": {"level": "beginner"},
        }

        self.collection.insert_document(original)

        self.assertEqual(original, original_before)
        self.assertNotIn("_id", original)


class TestRetrieveDocument(unittest.TestCase):
    """Test retrieval of documents from a Collection."""

    def setUp(self):
        self.db = AtlasDB()
        self.collection = self.db.collection("test_collection")

    def test_retrieve_existing_document(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        retrieved = self.collection.retrieve_document(document_id)

        self.assertEqual(retrieved["name"], "sett")
        self.assertEqual(retrieved["age"], 30)
        self.assertEqual(retrieved["_id"], document_id)

    def test_retrieve_nonexistent_document_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.collection.retrieve_document("nonexistent-id")

    def test_retrieve_with_non_string_id_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.collection.retrieve_document(123)

    def test_retrieve_with_empty_string_id_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.collection.retrieve_document("")

    def test_retrieve_with_none(self):
        with self.assertRaises(TypeError):
            self.collection.retrieve_document(None)

    def test_retrieve_returns_deepcopy(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        retrieved = self.collection.retrieve_document(document_id)
        retrieved["name"] = "modified"

        original = self.collection._documents[document_id]
        self.assertEqual(original["name"], "sett")


class TestUpdateDocument(unittest.TestCase):
    """Test updating documents in a Collection."""

    def setUp(self):
        self.db = AtlasDB()
        self.collection = self.db.collection("test_collection")

    def test_update_existing_document(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        updates = {"age": 31, "city": "New York"}
        updated_document = self.collection.update_document(
            document_id, updates
        )

        self.assertEqual(updated_document["age"], 31)
        self.assertEqual(updated_document["city"], "New York")
        self.assertEqual(updated_document["_id"], document_id)

    def test_update_nonexistent_document_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.collection.update_document(
                "nonexistent-id", {"age": 31}
            )

    def test_update_with_empty_updates_continues_regularly(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        updated_document = self.collection.update_document(
            document_id, {}
        )

        self.assertEqual(updated_document["name"], "sett")
        self.assertEqual(updated_document["age"], 30)

    def test_update_with_non_string_id_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.collection.update_document(123, {"age": 31})

    def test_update_with_empty_string_id_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.collection.update_document("", {"age": 31})

    def test_update_with_none_id_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.collection.update_document(None, {"age": 31})

    def test_update_the_id_should_raise_ValueError(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        with self.assertRaises(ValueError):
            self.collection.update_document(
                document_id, {"_id": "new-id"}
            )

    def test_update_with_non_dict_updates_raises_typeerror(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        with self.assertRaises(TypeError):
            self.collection.update_document(
                document_id, ["age", 31]
            )

    def test_update_with_invalid_updates_raises_typeerror(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        with self.assertRaises(TypeError):
            self.collection.update_document(
                document_id, {"skills": {"Python", "Go"}}
            )

    def test_update_returns_deepcopy(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        updates = {"age": 31}
        updated_document = self.collection.update_document(
            document_id, updates
        )

        updated_document["age"] = 32

        original = self.collection._documents[document_id]
        self.assertEqual(original["age"], 31)


class TestDeleteDocument(unittest.TestCase):
    """Test deletion of documents from a Collection."""

    def setUp(self):
        self.db = AtlasDB()
        self.collection = self.db.collection("test_collection")

    def test_delete_existing_document(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        self.collection.delete_document(document_id)

        with self.assertRaises(KeyError):
            self.collection.retrieve_document(document_id)

    def test_delete_nonexistent_document_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.collection.delete_document("nonexistent-id")

    def test_delete_with_non_string_id_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.collection.delete_document(123)

    def test_delete_with_empty_string_id_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.collection.delete_document("")

    def test_delete_with_none_id_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.collection.delete_document(None)

    def test_delete_removes_document_from_storage(self):
        document = {"name": "sett", "age": 30}
        document_id = self.collection.insert_document(document)

        self.collection.delete_document(document_id)

        self.assertNotIn(document_id, self.collection._documents)

    
    def test_update_does_not_retain_references_to_nested_values(self):
        document_id = self.collection.insert_document(
            {"name": "sett"}
        )

        updates = {
            "settings": {"theme": "dark"},
            "tags": ["database"],
        }

        self.collection.update_document(document_id, updates)

        # Modify the original updates after the operation.
        updates["settings"]["theme"] = "light"
        updates["tags"].append("modified")

        stored = self.collection.retrieve_document(document_id)

        self.assertEqual(stored["settings"], {"theme": "dark"})
        self.assertEqual(stored["tags"], ["database"])


if __name__ == "__main__":
    unittest.main()
