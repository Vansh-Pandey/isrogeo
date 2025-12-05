from fastapi import Request, HTTPException, status
from typing import Optional
from src.lib.utils import verify_token
from src.lib.db import get_database, USERS_COLLECTION
from bson import ObjectId

async def get_current_user(request: Request) -> dict:
    """
    Middleware to get current authenticated user from JWT cookie
    
    Args:
        request: FastAPI Request object
        
    Returns:
        dict: User data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = request.cookies.get("jwt")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - No token provided"
        )
    
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("userId")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    db = get_database()
    user = await db[USERS_COLLECTION].find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.pop("password", None)
    user["_id"] = str(user["_id"])
    
    return user

async def optional_auth(request: Request) -> Optional[dict]:
    """
    Optional authentication middleware
    Returns user if authenticated, None otherwise
    """
    try:
        return await get_current_user(request)
    except HTTPException:
        return None
