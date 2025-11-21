import json
import time
import pandas as pd
import pickle
import xgboost

with open(r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\models\model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

with open(r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\data\output.jsonl','r+') as file:
    data = file.readlines()
    records = [json.loads(data[-1])]
    df = pd.DataFrame(records)
    x = df[['amount','distance_from_home_km']]
    print(loaded_model.predict(x))
    
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
                return loaded_model.predict(x)

