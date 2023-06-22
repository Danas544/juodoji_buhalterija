# pylint: disable-all
from typing import Any, List, Optional, Union, Dict
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    PyMongoError,
    ServerSelectionTimeoutError,
    CollectionInvalid,
    ExecutionTimeout,
    OperationFailure,
)
from db_rules import insert_invoice_rule


class Base:
    def __init__(self) -> Any:
        self.client = MongoClient(
            "mongodb://localhost:27017/", serverSelectionTimeoutMS=5000
        )

    def get_db(self, db: str) -> Optional[MongoClient]:
        try:
            self.db = self.client[db]
            self.client.server_info()
            return self.db

        except ServerSelectionTimeoutError as e:
            print("Connection failure:", str(e))
            raise Exception("Connection failure")

        except PyMongoError as e:
            print("An error occurred:", str(e))
            exit()

    def execute_with_retry(self, func, db):
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                live_db = func(db)
                return live_db
            except Exception as e:
                print(f"Execution failed: {e}")
                retries += 1
                print(f"Retrying... (Attempt {retries}/{max_retries})")
                time.sleep(1)
        else:
            print("Maximum retries exceeded. Giving up.")
            exit()


class Collections(Base):
    def __init__(self, db: str, collection: str = None) -> Any:
        super().__init__()
        self.db = self.execute_with_retry(self.get_db, db)
        self.collection_name = collection
        self.collection = self.db[self.collection_name]

    def connect_validation_rule(self) -> str:
        try:
            self.db.command("collMod", self.collection.name, **insert_invoice_rule())
        except OperationFailure as e:
            print(f"Failed to enable schema validation: {e}")

    def create_document(self, task: Dict[str, Any]) -> str:
        self.connect_validation_rule()
        result = self.collection.insert_one(task)
        return str(result.inserted_id)
