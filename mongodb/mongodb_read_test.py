from pymongo import MongoClient

def read_from_mongo():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["your_database_name"]
    collection = db["your_collection_name"]

    # Find all documents in the collection
    documents = collection.find()

    # Print each document
    for document in documents:
        print(document)

if __name__ == "__main__":
    read_from_mongo()
