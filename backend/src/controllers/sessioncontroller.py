from fastapi import HTTPException, status
from modals.sessionmodel import SessionCreate, SessionUpdate
from lib.db import get_database, SESSIONS_COLLECTION
from bson import ObjectId
from datetime import datetime
import secrets


def serialize_session(session: dict) -> dict:
    """
    Serialize session document to ensure _id is a string
    
    Args:
        session: Session document from MongoDB
        
    Returns:
        dict: Serialized session with _id as string
    """
    if not session:
        return None
    
    # Convert ObjectId to string
    if "_id" in session and isinstance(session["_id"], ObjectId):
        session["_id"] = str(session["_id"])
    
    return session

 

async def create_session(user_id: str, session_data: SessionCreate) -> dict:
    """
    Create a new session
    
    Args:
        user_id: User's ID
        session_data: Session creation data
        
    Returns:
        dict: Created session data with _id as string
    """
    db = get_database()
    
    session_dict = {
        "userId": user_id,
        "name": session_data.name,
        "archived": session_data.archived,
        "projectId": session_data.projectId,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db[SESSIONS_COLLECTION].insert_one(session_dict)
    
    created_session = await db[SESSIONS_COLLECTION].find_one({"_id": result.inserted_id})
    
    # Serialize and ensure _id exists
    serialized_session = serialize_session(created_session)
    
    print(f"✅ Created session: {serialized_session['_id']} - {serialized_session['name']}")
    
    return serialized_session


async def get_user_sessions(user_id: str) -> list:
    """
    Get all sessions for a user
    
    Args:
        user_id: User's ID
        
    Returns:
        list: List of sessions with _id as string
    """
    db = get_database()
    
    cursor = db[SESSIONS_COLLECTION].find({"userId": user_id}).sort("updatedAt", -1)
    sessions = await cursor.to_list(length=None)
    
    # Serialize all sessions
    serialized_sessions = []
    for session in sessions:
        serialized = serialize_session(session)
        if serialized:
            serialized_sessions.append(serialized)
            print(f"🔍 Session: {serialized['_id']} - {serialized['name']}")
    
    print(f"📊 Total sessions for user {user_id}: {len(serialized_sessions)}")
    
    return serialized_sessions


async def get_session_by_id(session_id: str, user_id: str) -> dict:
    """
    Get a specific session by ID
    
    Args:
        session_id: Session ID
        user_id: User's ID
        
    Returns:
        dict: Session data with _id as string
        
    Raises:
        HTTPException: If session not found or unauthorized
    """
    db = get_database()
    
    if not ObjectId.is_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID"
        )
    
    session = await db[SESSIONS_COLLECTION].find_one({
        "_id": ObjectId(session_id),
        "userId": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return serialize_session(session)


async def update_session(session_id: str, user_id: str, update_data: SessionUpdate) -> dict:
    """
    Update a session
    
    Args:
        session_id: Session ID
        user_id: User's ID
        update_data: Data to update
        
    Returns:
        dict: Updated session data with _id as string
        
    Raises:
        HTTPException: If session not found or no data to update
    """
    db = get_database()
    
    if not ObjectId.is_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID"
        )
    
    update_dict = update_data.dict(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    update_dict["updatedAt"] = datetime.utcnow()
    
    result = await db[SESSIONS_COLLECTION].find_one_and_update(
        {"_id": ObjectId(session_id), "userId": user_id},
        {"$set": update_dict},
        return_document=True
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    serialized_result = serialize_session(result)
    print(f"✅ Updated session: {serialized_result['_id']} - {serialized_result['name']}")
    
    return serialized_result


async def delete_session(session_id: str, user_id: str) -> dict:
    """
    Delete a session
    
    Args:
        session_id: Session ID
        user_id: User's ID
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If session not found
    """
    db = get_database()
    
    if not ObjectId.is_valid(session_id):
        print(f"❌ Invalid session ID format: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID"
        )
    
    # First, verify the session exists and belongs to the user
    session = await db[SESSIONS_COLLECTION].find_one({
        "_id": ObjectId(session_id),
        "userId": user_id
    })
    
    if not session:
        print(f"❌ Session not found or unauthorized: {session_id} for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    print(f"🗑️ Deleting session: {session_id} - {session.get('name', 'Unknown')}")
    
    # Delete the session
    result = await db[SESSIONS_COLLECTION].delete_one({
        "_id": ObjectId(session_id),
        "userId": user_id
    })
    
    if result.deleted_count == 0:
        print(f"❌ Failed to delete session: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Also delete associated messages and images
    from lib.db import MESSAGES_COLLECTION, IMAGES_COLLECTION
    
    messages_deleted = await db[MESSAGES_COLLECTION].delete_many({"sessionId": session_id})
    images_deleted = await db[IMAGES_COLLECTION].delete_many({"sessionId": session_id})
    
    print(f"✅ Deleted session: {session_id}")
    print(f"   - Messages deleted: {messages_deleted.deleted_count}")
    print(f"   - Images deleted: {images_deleted.deleted_count}")
    
    return {"message": "Session deleted successfully"}


async def share_session(session_id: str, user_id: str) -> dict:
    """
    Generate a share link for a session
    
    Args:
        session_id: Session ID
        user_id: User's ID
        
    Returns:
        dict: Share link
        
    Raises:
        HTTPException: If session not found
    """
    db = get_database()
    
    if not ObjectId.is_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID"
        )
    
    session = await db[SESSIONS_COLLECTION].find_one({
        "_id": ObjectId(session_id),
        "userId": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Generate a unique share token
    share_token = secrets.token_urlsafe(32)
    
    # Update session with share token
    await db[SESSIONS_COLLECTION].update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"shareToken": share_token, "sharedAt": datetime.utcnow()}}
    )
    
    # In production, this should be your actual domain
    share_link = f"https://yourdomain.com/shared/{share_token}"
    
    print(f"🔗 Generated share link for session: {session_id}")
    
    return {"shareLink": share_link}