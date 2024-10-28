from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

def connectToPinecone():
    try:
        api_key = os.getenv("PINECONE_KEYV2")
        print(api_key)
        pc = Pinecone(api_key=api_key)
        print("Connected to Pinecone")
        return pc
    except Exception as e:
        print(f"Error connecting to Pinecone: {e}")
        return None
    
if __name__ == "__main__":
    connectToPinecone()