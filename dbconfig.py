
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def connectToDB():
    try:
        mongo_uri = os.getenv("MONGO_URI")
        client = MongoClient(mongo_uri, tlsInsecure =True)
        database = client.get_database("pairit")
        collection = database.get_collection("classes")
        print("Connected to database")
        return collection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

if __name__ == "__main__":
    connectToDB()