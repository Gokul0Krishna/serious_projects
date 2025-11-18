from pymongo import MongoClient, UpdateOne
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")     
db = client["bitcoin_data"]
collection = db["prices"]

def Insert(df):
    operations = []

    for _, row in df.iterrows():
        doc = {
            "ticker": row["ticker"],
            "date": row["date"],                      
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "adj_close": float(row["Adj Close"]),
            "volume": int(row["Volume"]),
            "ingested_at": datetime.utcnow()
        }

        operations.append(
            UpdateOne(
                {"ticker": row["ticker"], "date": row["date"]},
                {"$set": doc},
                upsert=True
            )
        )

    if operations:
        result = collection.bulk_write(operations)
        print(f"Inserted: {result.upserted_count}, Modified: {result.modified_count}")