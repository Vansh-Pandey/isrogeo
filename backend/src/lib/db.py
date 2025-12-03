from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "geonli_db")

# Collection Names
USERS_COLLECTION = "users"
SESSIONS_COLLECTION = "sessions"
PROJECTS_COLLECTION = "projects"
MESSAGES_COLLECTION = "messages"
IMAGES_COLLECTION = "images"

# Global client variable
_client = None
_database = None


def get_client():
    """Get or create MongoDB client"""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URL)
    return _client


def get_database():
    """Get or create database instance"""
    global _database
    if _database is None:
        client = get_client()
        _database = client[DATABASE_NAME]
    return _database


async def close_database():
    """Close database connection"""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None


async def init_database():
    """Initialize database and create indexes"""
    db = get_database()
    
    # Create indexes for users collection
    await db[USERS_COLLECTION].create_index("email", unique=True)
    await db[USERS_COLLECTION].create_index("createdAt")
    
    # Create indexes for sessions collection
    await db[SESSIONS_COLLECTION].create_index([("userId", 1), ("updatedAt", -1)])
    await db[SESSIONS_COLLECTION].create_index("projectId")
    await db[SESSIONS_COLLECTION].create_index("archived")
    
    # Create indexes for projects collection
    await db[PROJECTS_COLLECTION].create_index([("userId", 1), ("createdAt", -1)])
    
    # Create indexes for messages collection
    await db[MESSAGES_COLLECTION].create_index([("sessionId", 1), ("createdAt", 1)])
    await db[MESSAGES_COLLECTION].create_index("userId")
    await db[MESSAGES_COLLECTION].create_index("sender")
    
    # Create indexes for images collection
    await db[IMAGES_COLLECTION].create_index([("sessionId", 1), ("uploadedAt", -1)])
    await db[IMAGES_COLLECTION].create_index("userId")
    
    print("Database indexes created successfully")