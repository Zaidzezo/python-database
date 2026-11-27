import os
import json
import shutil
import tempfile
import unittest

from storage import load_documents, save_documents
from atlasdb import AtlasDB


class TestStorage(unittest.TestCase):
    def setUp(self):
        self._original_cwd = os.getcwd()
        self._temp_dir = tempfile.mkdtemp()
        os.chdir(self._temp_dir)

    def tearDown(self):
        os.chdir(self._original_cwd)
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    # --- load_documents ---

    def test_load_nonexistent_collection_returns_empty_dict(self):
        result = load_documents("does_not_exist")
        self.assertEqual(result, {})

    def test_load_does_not_create_a_file(self):
        load_documents("does_not_exist")
        self.assertFalse(os.path.exists(os.path.join("data", "does_not_exist.json")))

    # --- save_documents: basic behavior ---

    def test_save_creates_data_directory(self):
        self.assertFalse(os.path.exists("data"))
        save_documents("users", {"1": {"_id": "1", "name": "Ali"}})
        self.assertTrue(os.path.isdir("data"))

    def test_save_creates_file_with_correct_name(self):
        save_documents("users", {})
        self.assertTrue(os.path.exists(os.path.join("data", "users.json")))

    def test_save_writes_correct_content(self):
        documents = {"1": {"_id": "1", "name": "Ali", "age": 16}}
        save_documents("users", documents)

        with open(os.path.join("data", "users.json")) as f:
            on_disk = json.load(f)

        self.assertEqual(on_disk, documents)

    def test_save_does_not_leave_temp_file_behind(self):
        save_documents("users", {"1": {"_id": "1"}})
        self.assertFalse(os.path.exists(os.path.join("data", "users.json.tmp")))

    def test_save_overwrites_rather_than_merges(self):
        save_documents("users", {"1": {"_id": "1", "name": "Ali"}})
        save_documents("users", {"2": {"_id": "2", "name": "Sara"}})

        with open(os.path.join("data", "users.json")) as f:
            on_disk = json.load(f)

        # The old "1" entry must be gone, not merged in alongside "2".
        self.assertEqual(on_disk, {"2": {"_id": "2", "name": "Sara"}})

    # --- round trip ---

    def test_save_then_load_round_trip(self):
        documents = {
            "1": {"_id": "1", "name": "Ali", "active": True, "tags": [1, 2, 3]},
        }
        save_documents("users", documents)
        loaded = load_documents("users")
        self.assertEqual(loaded, documents)

    def test_save_then_load_empty_dict(self):
        save_documents("users", {})
        loaded = load_documents("users")
        self.assertEqual(loaded, {})


class TestCollectionPersistsAcrossRestart(unittest.TestCase):
    """
    Integration-level checks: these go through Collection/AtlasDB, not
    storage.py directly, to confirm insert/update/delete actually call
    save_documents at the right point -- not just that storage.py itself
    works in isolation.
    """

    def setUp(self):
        self._original_cwd = os.getcwd()
        self._temp_dir = tempfile.mkdtemp()
        os.chdir(self._temp_dir)

    def tearDown(self):
        os.chdir(self._original_cwd)
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    def test_inserted_document_survives_simulated_restart(self):
        db1 = AtlasDB()
        users1 = db1.collection("users")
        doc_id = users1.insert_document({"name": "Ali"})

        # Simulate a restart: a brand-new AtlasDB/Collection, not a reused
        # in-memory object, so this only passes if data actually came off disk.
        db2 = AtlasDB()
        users2 = db2.collection("users")

        retrieved = users2.retrieve_document(doc_id)
        self.assertEqual(retrieved["name"], "Ali")

    def test_updated_document_survives_simulated_restart(self):
        db1 = AtlasDB()
        users1 = db1.collection("users")
        doc_id = users1.insert_document({"name": "Ali", "age": 16})
        users1.update_document(doc_id, {"age": 17})

        db2 = AtlasDB()
        users2 = db2.collection("users")

        retrieved = users2.retrieve_document(doc_id)
        self.assertEqual(retrieved["age"], 17)

    def test_deleted_document_stays_deleted_after_simulated_restart(self):
        db1 = AtlasDB()
        users1 = db1.collection("users")
        doc_id = users1.insert_document({"name": "Ali"})
        users1.delete_document(doc_id)

        db2 = AtlasDB()
        users2 = db2.collection("users")

        with self.assertRaises(KeyError):
            users2.retrieve_document(doc_id)


if __name__ == "__main__":
    unittest.main()