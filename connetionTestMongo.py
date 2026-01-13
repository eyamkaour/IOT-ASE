# test_connection.py
import os
from pymongo import MongoClient

def test_connection():
    mongodb_url = "mongodb+srv://user2:Flg3UgvrCwe2usZC@cluster0.wa1xrm8.mongodb.net/?appName=Cluster0"
    
    try:
        client = MongoClient(mongodb_url, tls=True, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.admin.command('ping')
        print("✅ Connection successful!")
        
        # List databases
        databases = client.list_database_names()
        print(f"Available databases: {databases}")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()