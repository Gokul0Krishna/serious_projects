import json
import time
import pandas as pd
import pickle
import xgboost
import redis
from pymongo import MongoClient
import logging

LOG = logging.getLogger(__name__)
            
class Consumer():
    def __init__(self):

        LOG.info("Loading model1...")   
        with open(r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\models\model2.pkl', 'rb') as file:
                self.model = pickle.load(file)

        LOG.info("Connecting to Redis...")
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.group = "fraud_group"
        self.consumer = "consumer_1"
        try:
            self.redis.xgroup_create("transactions", self.group, id="0", mkstream=True)
        except:
            pass 

        LOG.info("Connecting to DB...")
        client = MongoClient("mongodb://localhost:27017")
        db = client["fraud_detection"]  
        self.fraud_collection = db["fraud_tx"]
        
    def run(self):
        while True:
            msgs = self.redis.xreadgroup(
                groupname=self.group,
                consumername=self.consumer,
                streams={"transactions": ">"},
                count=1,
                block=5000
            )
            for stream, entries in msgs:
                for msg_id, msg_data in entries:

                    tx = json.loads(msg_data["json"])

                    df = pd.DataFrame([tx])
                    x = df[['amount', 'distance_from_home_km']]

                    pred = self.model.predict(x)[0]
                    if pred == 1:
                        self.fraud_collection.insert_one(tx)
                    self.redis.xack("transactions", self.group, msg_id)

def cmain():
    obj = Consumer()
    obj.run()

if __name__ == '__main__':
    cmain()