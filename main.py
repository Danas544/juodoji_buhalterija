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
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
import json


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
    def __init__(self, db: str, collection: str = None) -> None:
        super().__init__()
        self.db = self.execute_with_retry(self.get_db, db)
        self.collection_name = collection
        self.collection = self.db[self.collection_name]

    def get_collection(self):
        return self.collection

    def connect_validation_rule(self) -> str:
        try:
            self.db.command("collMod", self.collection.name, **insert_invoice_rule())
        except OperationFailure as e:
            print(f"Failed to enable schema validation: {e}")

    def create_document(self, task: Dict[str, Any]) -> str:
        self.connect_validation_rule()
        result = self.collection.insert_one(task)
        return str(result.inserted_id)


class Pipeline_search(Collections):
    def __init__(
        self, collection: Collection, criteria: List[Dict[str, Any]] = None
    ) -> None:
        self.criteria = criteria
        self.collection = collection

    def filter_documents_match(self) -> Cursor:
        pipeline = [{"$match": {"$and": self.criteria}}]
        return self.collection.aggregate(pipeline)

    def sort_documents(self) -> Cursor:
        pipeline = [{"$sort": self.criteria}]
        return self.collection.aggregate(pipeline)

    def project_documents(self) -> Cursor:
        pipeline = [{"$project": self.criteria}]
        return self.collection.aggregate(pipeline)

    def aggregate_documents(self, pipeline: Dict[str, Any]) -> Cursor:
        return self.collection.aggregate(pipeline)


if "__main__" == __name__:
    db = Collections(db="black_database", collection="invoices")

    collection = db.get_collection()

    schema_match = [
        {"invoice_details.tax": 21},
        {
            "$or": [
                {"invoice_details.buyer_name": "python"},
                {"invoice_details.buyer_name": "mammal"},
            ]
        },
    ]

    search1 = Pipeline_search(criteria=schema_match, collection=collection)
    match_document = search1.filter_documents_match()
    for x in match_document:
        print(x)


schema_sort: Dict[str, int] = {
    "Date": 1,
    "invoice_number": 1,
}
sort = Pipeline_search(criteria=schema_sort, collection=collection)
sort_document = sort.sort_documents()
for x in sort_document:
    print(x)

schema_project: Dict[str, int] = {
    "invoice_number": 1,
    "invoice_details.buyer_name": 1,
    "invoice_details.goods.name": 1,
}

schema_projection = Pipeline_search(criteria=schema_project, collection=collection)
for x in schema_projection.project_documents():
    print(x)


pipline: Dict[str, Any] = [
    {
        "$match": {
            "$and": [
                {"invoice_details.tax": 21},
                {
                    "$or": [
                        {"invoice_details.buyer_name": "python"},
                        {"invoice_details.buyer_name": "mammal"},
                        {"invoice_details.price": {"$gte": 70000}},
                    ]
                },
            ],
        }
    },
    {"$sort": {"invoice_details.price_with_tax": -1}},
    {
        "$project": {
            "_id": 0,
            "invoice_number": 1,
            "invoice_details.price_with_tax": 1,
            "invoice_details.buyer_name": 1,
        }
    },
]

aggregate = Pipeline_search(collection=collection)
for x in aggregate.aggregate_documents(pipeline=pipline):
    print(json.dumps(x, indent=2))
