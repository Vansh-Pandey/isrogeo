from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Response
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 2

def generate_token(user_id: str, response: Response) -> str:
    """
    Generate JWT token and set it as an HTTP-only cookie
    
    Args:
        user_id: User's unique identifier
        response: FastAPI Response object to set cookie
        
    Returns:
        str: Generated JWT token
    """
    expires_delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "userId": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    max_age = ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    
    response.set_cookie(
        key="jwt",
        value=token,
        max_age=max_age,
        httponly=True,
        samesite="strict",
        secure=os.getenv("NODE_ENV") != "development"
    )
    
    return token

def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None

def clear_token(response: Response):
    """
    Clear JWT token cookie
    
    Args:
        response: FastAPI Response object
    """
    response.delete_cookie(
        key="jwt",
        httponly=True,
        samesite="strict",
        secure=os.getenv("NODE_ENV") != "development"
    )
