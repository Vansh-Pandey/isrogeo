from fastapi import HTTPException, status, Response
from passlib.context import CryptContext
from src.modals.usermodel import UserCreate, UserLogin, UpdateProfile
from src.lib.db import get_database, USERS_COLLECTION
from src.lib.utils import generate_token, clear_token
from bson import ObjectId
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def signup(user_data: UserCreate, response: Response) -> dict:
    db = get_database()
    
    existing_user = await db[USERS_COLLECTION].find_one({"email": user_data.email})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = hash_password(user_data.password)
    
    user_dict = {
        "email": user_data.email,
        "fullName": user_data.fullName,
        "password": hashed_password,
        "profilePic": None,
        "createdAt": datetime.utcnow()
    }
    
    result = await db[USERS_COLLECTION].insert_one(user_dict)
    user_id = str(result.inserted_id)
    
    generate_token(user_id, response)
    
    created_user = await db[USERS_COLLECTION].find_one({"_id": result.inserted_id})
    
    created_user.pop("password", None)
    created_user["_id"] = str(created_user["_id"])
    
    return created_user

async def login(user_data: UserLogin, response: Response) -> dict:
    db = get_database()
    
    user = await db[USERS_COLLECTION].find_one({"email": user_data.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )
    
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )
    
    user_id = str(user["_id"])
    generate_token(user_id, response)
    
    user.pop("password", None)
    user["_id"] = str(user["_id"])
    
    return user

async def logout(response: Response) -> dict:
    clear_token(response)
    return {"message": "Logged out successfully"}

async def check_auth(user: dict) -> dict:
    return user

async def update_profile(user_id: str, update_data: dict) -> dict:
    db = get_database()
    
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    result = await db[USERS_COLLECTION].find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result.pop("password", None)
    result["_id"] = str(result["_id"])
    
    return result
