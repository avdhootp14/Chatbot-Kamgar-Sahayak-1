# create_initial_admin_bcrypt.py
import pymongo
from pymongo import MongoClient
from passlib.context import CryptContext

# --- MongoDB connection ---
MONGO_URI = "mongodb+srv://xiaa:dnAHHT69ejGQ1lSK@clutter.3ary0d9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

# --- Choose the correct DB and collection ---
admin_db = client["admin_db"]
admins_collection = admin_db["admins"]

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Admin credentials ---
admin_email = "admin@example.com"
admin_password = "Admin@123"

# --- Hash the password using bcrypt ---
hashed_password = pwd_context.hash(admin_password)

# --- Insert admin if not exists ---
if admins_collection.find_one({"email": admin_email}):
    print(f"Admin with email {admin_email} already exists.")
else:
    admins_collection.insert_one({
        "email": admin_email,
        "hashed_password": hashed_password,
        "role": "admin"  # must match your login code field
    })
    print(f"Admin {admin_email} added successfully to admin_db.admins.")
