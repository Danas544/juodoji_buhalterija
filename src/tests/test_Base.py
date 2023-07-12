import unittest
from unittest.mock import MagicMock
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from main import Base

class TestBase(unittest.TestCase):
    def setUp(self):
        self.client_mock = MagicMock(MongoClient)
        self.base = Base()
        self.base.client = self.client_mock

    def test_get_db_success(self):
        db_name = "test_db"
        db_mock = MagicMock()
        self.client_mock.__getitem__.return_value = db_mock

        result = self.base.get_db(db_name)

        self.assertEqual(result, db_mock)
        
        

    def test_get_db_timeout_error(self):
        db_name = "test_db"
        self.client_mock.server_info.side_effect = ServerSelectionTimeoutError("timeout")

        with self.assertRaises(Exception) as context:
            self.base.get_db(db_name)

        self.assertIn("Connection failure: timeout", str(context.exception))
        self.client_mock.server_info.assert_called_once()

    def test_get_db_mongo_error(self):
        db_name = "test_db"
        self.client_mock.server_info.side_effect = Exception("mongo error")

        with self.assertRaises(Exception) as context:
            self.base.get_db(db_name)

        self.assertTrue("mongo error" in str(context.exception))
        self.client_mock.server_info.assert_called_once()


    def test_execute_with_retry_success(self):
        mock_func = MagicMock(return_value="success")

        result = self.base.execute_with_retry(mock_func, "test_db")

        self.assertEqual(result, "success")
        mock_func.assert_called_once_with("test_db")

    def test_execute_with_retry_exception(self):
        mock_func = MagicMock(side_effect=[Exception("error1"), Exception("error2"), "success"])

        result = self.base.execute_with_retry(mock_func, "test_db")

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 3)
        mock_func.assert_called_with("test_db")

    def test_execute_with_retry_max_retries_exceeded(self):
        mock_func = MagicMock(side_effect=Exception("error"))

        with self.assertRaises(Exception) as context:
            self.base.execute_with_retry(mock_func, "test_db")

        self.assertIn("Maximum retries exceeded", str(context.exception))
        self.assertEqual(mock_func.call_count, 3)
        mock_func.assert_called_with("test_db")


if __name__ == "__main__":
    unittest.main()