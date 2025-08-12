import logging
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import bcrypt

logger = logging.getLogger(__name__)

client: Optional[MongoClient] = None
db = None

async def connect_to_mongo(mongo_uri: str, db_name: str):
    global client, db
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[db_name]
        logger.info("✅ Connected to MongoDB.")
    except ConnectionFailure as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error connecting to MongoDB: {e}", exc_info=True)
        raise

async def close_mongo_connection():
    global client
    if client:
        client.close()
        logger.info("🔌 MongoDB connection closed.")

def get_mongo_db():
    if db is None:
        raise ConnectionFailure("MongoDB connection not established.")
    return db

def get_all_faqs() -> List[Dict[str, Any]]:
    db = get_mongo_db()
    faqs = list(db["faqs"].find({}, {"_id": 0}))  # Exclude _id for cleaner data
    logger.info(f"Fetched {len(faqs)} FAQs from MongoDB.")
    return faqs

async def insert_log_entry(entry: Dict[str, Any]) -> str:
    try:
        logs_collection = get_mongo_db()["logs"]
        result = logs_collection.insert_one(entry)
        logger.info(f"📝 Log entry inserted with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting log entry: {e}", exc_info=True)
        raise

async def create_user(user_data: Dict[str, Any]) -> str:
    try:
        users_collection = get_mongo_db()["users"]

        if users_collection.find_one({"email": user_data["email"]}):
            raise ValueError("Email already registered")

        hashed_pw = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
        user_data["password"] = hashed_pw.decode('utf-8')

        result = users_collection.insert_one(user_data)
        logger.info(f"👤 User registered with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    try:
        users_collection = get_mongo_db()["users"]
        return users_collection.find_one({"email": email})
    except Exception as e:
        logger.error(f"Error fetching user by email: {e}", exc_info=True)
        raise

async def verify_user(email: str, password: str) -> bool:
    try:
        user = await get_user_by_email(email)
        if not user:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8'))
    except Exception as e:
        logger.error(f"Error verifying user: {e}", exc_info=True)
        raise

def get_unanswered_logs() -> List[Dict[str, Any]]:
    db = get_mongo_db()
    return list(db["logs"].find({"answer": None}))

def get_all_logs_entries() -> List[Dict[str, Any]]:
    db = get_mongo_db()
    return list(db["logs"].find({}))

async def get_admin_user(username: str) -> Optional[Dict[str, Any]]:
    db = get_mongo_db()
    return db["admins"].find_one({"username": username})

async def create_admin_user(admin_data: Dict[str, Any]) -> str:
    db = get_mongo_db()
    result = db["admins"].insert_one(admin_data)
    return str(result.inserted_id)
