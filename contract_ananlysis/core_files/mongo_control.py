from pymongo import MongoClient
from datetime import datetime
import uuid

class Mongo_control():
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["contract_analysis"]
        self.collection = self.db["contracts"]
    
    def save_contract(self, contract_obj, filename, source="UNKNOWN"):
        document = {
            "contract_id": contract_obj["contract_id"],
            "filename": filename,
            "source": source,
            "version": 1,
            "uploaded_at": datetime.utcnow(),
            "sections": contract_obj["sections"]
        }

        result = self.collection.insert_one(document)
        return str(result.inserted_id)

if __name__ == '__main__':
    obj = Mongo_control()