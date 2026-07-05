import pymongo
from src.config import MONGODB_URI

_client = None

def get_client():
    """Returns a singleton MongoClient instance."""
    global _client
    if _client is None:
        _client = pymongo.MongoClient(MONGODB_URI)
    return _client

def get_db():
    """Returns the database instance from the client, defaulting to database 'tbe' if not specified in URI."""
    client = get_client()
    try:
        db = client.get_default_database()
        if db is None:
            db = client['tbe']
    except Exception:
        db = client['tbe']
    return db

COLLECTIONS = [
    "candidates",
    "evaluations",
    "trades",
    "portfolio_state",
    "stats_aggregates",
    "audit_log"
]

def init_db():
    """Pings MongoDB and initializes the required collections if they do not exist."""
    db = get_db()
    
    try:
        # Check connection using admin command ping
        db.client.admin.command('ping')
        print("Database connection verified successfully via ping.")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to MongoDB Atlas: {e}")
        
    existing = db.list_collection_names()
    for col in COLLECTIONS:
        if col not in existing:
            db.create_collection(col)
            print(f"Collection '{col}' created successfully.")
        else:
            print(f"Collection '{col}' already exists.")
            
    print("Database initialization complete.")
