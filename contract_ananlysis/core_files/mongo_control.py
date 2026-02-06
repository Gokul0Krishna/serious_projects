from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
import uuid

class Mongo_control():
    def __init__(self):
        self.url = "mongodb://localhost:27017/"
        self.db_name = "contract_analysis"
        self.collection_name = "contracts"

        try:
            self.client = MongoClient(self.url, serverSelectionTimeoutMS=3000)
            self.client.admin.command("ping")
        except ConnectionFailure:
            raise RuntimeError("MongoDB server not reachable")
        self.db = self.client[self.db_name]

        if self.collection_name not in self.db.list_collection_names():
            self.collection = self.db.create_collection(self.collection_name)
        else:
            self.collection = self.db[self.collection_name]
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        # One document per contract
        self.collection.create_index(
            "contract_id",
            unique=True
        )

    def _show_all(self):
        return list(
            self.collection.find({})
        )
    
    def _clean(self):
        self.client.drop_database('contract_analysis')


    def save_contract(self, contract_obj, filename, source="UNKNOWN"):
        document = {
            "contract_id": contract_obj["contract_id"],
            "filename": filename,
            "source": source,
            "version": 1,
            "uploaded_at": datetime.utcnow(),
            "sections": contract_obj["section"]
        }

        result = self.collection.insert_one(document)
        return str(result.inserted_id)

if __name__ == '__main__':
    obj = Mongo_control()
    z = obj._check_working()
    print(z)
    # obj._clean()