from pymongo import MongoClient
from datetime import datetime
import calendar

def write_to_mongo():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["your_database_name"]
    collection = db["your_collection_name"]

    # Get the current date and its day name
    now = datetime.now()
    day_name = calendar.day_name[now.weekday()]

    # Create a document to insert
    document = {
        "date": now.strftime("%Y-%m-%d"),
        "day_name": day_name
    }

    # Insert the document into the collection
    result = collection.insert_one(document)
    print(f"Inserted document with ID: {result.inserted_id}")

if __name__ == "__main__":
    write_to_mongo()
