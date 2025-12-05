from fastapi import HTTPException, status
from src.modals.messagemodel import MessageCreate, AIResponseRequest
from src.lib.db import get_database, MESSAGES_COLLECTION, SESSIONS_COLLECTION
from bson import ObjectId
from datetime import datetime
import openai
import os


# Configure OpenAI (or your preferred AI service)
openai.api_key = os.getenv("OPENAI_API_KEY", "")


async def create_message(user_id: str, message_data: MessageCreate) -> dict:
    """
    Create a new message
    
    Args:
        user_id: User's ID
        message_data: Message creation data
        
    Returns:
        dict: Created message data
        
    Raises:
        HTTPException: If session not found
    """
    db = get_database()
    
    # Verify session exists and belongs to user
    if ObjectId.is_valid(message_data.sessionId):
        session = await db[SESSIONS_COLLECTION].find_one({
            "_id": ObjectId(message_data.sessionId),
            "userId": user_id
        })
    else:
        session = await db[SESSIONS_COLLECTION].find_one({
            "_id": message_data.sessionId,
            "userId": user_id
        })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    message_dict = {
        "sessionId": message_data.sessionId,
        "userId": user_id,
        "text": message_data.text,
        "sender": "user",
        "imageData": message_data.imageData,
        "timestamp": datetime.utcnow(),
        "createdAt": datetime.utcnow()
    }
    
    result = await db[MESSAGES_COLLECTION].insert_one(message_dict)
    
    # Update session's updatedAt
    if ObjectId.is_valid(message_data.sessionId):
        await db[SESSIONS_COLLECTION].update_one(
            {"_id": ObjectId(message_data.sessionId)},
            {"$set": {"updatedAt": datetime.utcnow()}}
        )
    
    created_message = await db[MESSAGES_COLLECTION].find_one({"_id": result.inserted_id})
    created_message["_id"] = str(created_message["_id"])
    
    return created_message


async def get_session_messages(session_id: str, user_id: str) -> list:
    """
    Get all messages for a session
    
    Args:
        session_id: Session ID
        user_id: User's ID
        
    Returns:
        list: List of messages
        
    Raises:
        HTTPException: If session not found
    """
    db = get_database()
    
    # Verify session exists and belongs to user
    if ObjectId.is_valid(session_id):
        session = await db[SESSIONS_COLLECTION].find_one({
            "_id": ObjectId(session_id),
            "userId": user_id
        })
    else:
        session = await db[SESSIONS_COLLECTION].find_one({
            "_id": session_id,
            "userId": user_id
        })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    cursor = db[MESSAGES_COLLECTION].find({"sessionId": session_id}).sort("createdAt", 1)
    messages = await cursor.to_list(length=None)
    
    for message in messages:
        message["_id"] = str(message["_id"])
    
    return messages


async def generate_ai_response(user_id: str, ai_request: AIResponseRequest) -> dict:
    """
    Generate AI response for a message
    
    Args:
        user_id: User's ID
        ai_request: AI response request data
        
    Returns:
        dict: Created AI message
        
    Raises:
        HTTPException: If session or message not found, or AI error
    """
    db = get_database()
    
    # Verify session exists
    if ObjectId.is_valid(ai_request.sessionId):
        session = await db[SESSIONS_COLLECTION].find_one({
            "_id": ObjectId(ai_request.sessionId),
            "userId": user_id
        })
    else:
        session = await db[SESSIONS_COLLECTION].find_one({
            "_id": ai_request.sessionId,
            "userId": user_id
        })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get the user's message
    if ObjectId.is_valid(ai_request.messageId):
        user_message = await db[MESSAGES_COLLECTION].find_one({
            "_id": ObjectId(ai_request.messageId)
        })
    else:
        user_message = await db[MESSAGES_COLLECTION].find_one({
            "_id": ai_request.messageId
        })
    
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Get conversation history
    cursor = db[MESSAGES_COLLECTION].find({
        "sessionId": ai_request.sessionId
    }).sort("createdAt", 1).limit(10)
    history = await cursor.to_list(length=None)
    
    # Build conversation context
    conversation = []
    for msg in history:
        role = "user" if msg["sender"] == "user" else "assistant"
        conversation.append({
            "role": role,
            "content": msg["text"]
        })
    
    try:
        # Generate AI response using OpenAI
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant specializing in satellite image analysis and geospatial intelligence."
                },
                *conversation
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_text = response.choices[0].message.content
        
    except Exception as e:
        print(f"AI Error: {str(e)}")
        # Fallback response if AI fails
        ai_text = "I'm sorry, I'm having trouble processing your request right now. Please try again."
    
    # Save AI response
    ai_message_dict = {
        "sessionId": ai_request.sessionId,
        "userId": user_id,
        "text": ai_text,
        "sender": "ai",
        "imageData": None,
        "timestamp": datetime.utcnow(),
        "createdAt": datetime.utcnow()
    }
    
    result = await db[MESSAGES_COLLECTION].insert_one(ai_message_dict)
    
    created_message = await db[MESSAGES_COLLECTION].find_one({"_id": result.inserted_id})
    created_message["_id"] = str(created_message["_id"])
    
    return created_message


async def delete_message(message_id: str, user_id: str) -> dict:
    """
    Delete a message
    
    Args:
        message_id: Message ID
        user_id: User's ID
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If message not found
    """
    db = get_database()
    
    if not ObjectId.is_valid(message_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID"
        )
    
    # Verify message belongs to user
    message = await db[MESSAGES_COLLECTION].find_one({
        "_id": ObjectId(message_id),
        "userId": user_id
    })
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    result = await db[MESSAGES_COLLECTION].delete_one({
        "_id": ObjectId(message_id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return {"message": "Message deleted successfully"}