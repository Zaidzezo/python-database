from atlasdb import AtlasDB
import unittest

class TestAtlasDB(unittest.TestCase):
    def setUp(self):
        self.db = AtlasDB()
    
    def test_collection_creation(self):
        collection_name = "test_collection"
        collection = self.db.collection(collection_name)
        self.assertEqual(collection.name, collection_name)

    def test_collection_retrieval(self):
        collection_name = "test_collection"
        collection1 = self.db.collection(collection_name)
        collection2 = self.db.collection(collection_name)
        self.assertIs(collection1, collection2)

    def test_invalid_collection_name(self):
        with self.assertRaises(TypeError):
            self.db.collection(123)

        with self.assertRaises(ValueError):
            self.db.collection("")

        with self.assertRaises(ValueError):
            self.db.collection("   ")

    def test_collection_isolation(self):
        users = self.db.collection("users")
        products = self.db.collection("products")

        document_id = users.insert_document({"name": "Zaid"})

        with self.assertRaises(KeyError):
            products.retrieve_document(document_id)

    def test_collection_name_whitespace(self):
        with self.assertRaises(ValueError):
            self.db.collection(" users ")

if __name__ == "__main__":
    unittest.main()
