import unittest
from unittest.mock import MagicMock
from pymongo.collection import Collection
from main import Collections


class TestCollections(unittest.TestCase):
    def setUp(self):
        self.db_name = "test_db"
        self.collection_name = "test_collection"
        self.collection_mock = MagicMock(Collection)
        self.collections = Collections(db=self.db_name, collection=self.collection_name)

    def test_get_collection(self):
        collection = self.collections.get_collection()
        self.assertIsInstance(collection, Collection)


if __name__ == "__main__":
    unittest.main()
