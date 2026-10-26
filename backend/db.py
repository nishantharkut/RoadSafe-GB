import os
from pymongo import MongoClient
from backend.config import Config

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        _db = _client[Config.DB_NAME]
    return _db

def check_connection():
    try:
        db = get_db()
        db.command("ping")
        return True, "Connected"
    except Exception as e:
        return False, str(e)
