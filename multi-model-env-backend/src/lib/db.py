from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "geonli_db")

USERS_COLLECTION = "users"
SESSIONS_COLLECTION = "sessions"
PROJECTS_COLLECTION = "projects"
MESSAGES_COLLECTION = "messages"
IMAGES_COLLECTION = "images"

_client = None
_database = None

def get_client():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URL)
    return _client

def get_database():
    global _database
    if _database is None:
        client = get_client()
        _database = client[DATABASE_NAME]
    return _database

async def close_database():
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None

async def init_database():
    db = get_database()
    await db[USERS_COLLECTION].create_index("email", unique=True)
    await db[USERS_COLLECTION].create_index("createdAt")
    await db[SESSIONS_COLLECTION].create_index([("userId", 1), ("updatedAt", -1)])
    await db[SESSIONS_COLLECTION].create_index("projectId")
    await db[SESSIONS_COLLECTION].create_index("archived")
    await db[PROJECTS_COLLECTION].create_index([("userId", 1), ("createdAt", -1)])
    await db[MESSAGES_COLLECTION].create_index([("sessionId", 1), ("createdAt", 1)])
    await db[MESSAGES_COLLECTION].create_index("userId")
    await db[MESSAGES_COLLECTION].create_index("sender")
    await db[IMAGES_COLLECTION].create_index([("sessionId", 1), ("uploadedAt", -1)])
    await db[IMAGES_COLLECTION].create_index("userId")
    print("Database indexes created successfully")
