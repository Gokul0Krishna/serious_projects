import json
import time
import pandas as pd
import pickle
import xgboost
import redis
    
class live_ped():
    def __init__(self):
        with open(r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\models\model.pkl', 'rb') as file:
            self.model = pickle.load(file)
    def run(self):
        while True:
            with open(r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\data\output.jsonl','r+') as file:
                data = file.readlines()
                records = [json.loads(data[-1])]
                df = pd.DataFrame(records)
                x = df[['amount','distance_from_home_km']]
                return self.model.predict(x)
            
class Consumer():
    def __init__(self):   
        with open(r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\models\model.pkl', 'rb') as file:
                self.model = pickle.load(file)
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.group = "fraud_group"
        self.consumer = "consumer_1"
        try:
            self.redis.xgroup_create("transactions", self.group, id="0", mkstream=True)
        except:
            pass 
    
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
                    self.redis.xack("transactions", self.group, msg_id)