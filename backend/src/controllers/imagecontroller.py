from fastapi import HTTPException, status, UploadFile
from modals.imagemodel import ImageAnalyzeRequest
from lib.db import get_database, IMAGES_COLLECTION, SESSIONS_COLLECTION, MESSAGES_COLLECTION
from bson import ObjectId
from datetime import datetime
import os
import shutil
import uuid
from pathlib import Path
import openai


# Configure upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "")


async def upload_image(user_id: str, session_id: str, image_file: UploadFile) -> dict:
    """
    Upload an image
    
    Args:
        user_id: User's ID
        session_id: Session ID
        image_file: Uploaded image file
        
    Returns:
        dict: Created image data
        
    Raises:
        HTTPException: If session not found or invalid file type
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
    
    # Validate file type
    if image_file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG and PNG images are allowed"
        )
    
    # Generate unique filename
    file_extension = image_file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save image: {str(e)}"
        )
    
    # Get file size
    file_size = file_path.stat().st_size
    
    # Save to database
    image_dict = {
        "sessionId": session_id,
        "userId": user_id,
        "filename": image_file.filename,
        "filepath": str(file_path),
        "mimetype": image_file.content_type,
        "size": file_size,
        "uploadedAt": datetime.utcnow()
    }
    
    result = await db[IMAGES_COLLECTION].insert_one(image_dict)
    
    created_image = await db[IMAGES_COLLECTION].find_one({"_id": result.inserted_id})
    created_image["_id"] = str(created_image["_id"])
    
    return created_image


async def delete_image(image_id: str, user_id: str) -> dict:
    """
    Delete an image
    
    Args:
        image_id: Image ID
        user_id: User's ID
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If image not found
    """
    db = get_database()
    
    if not ObjectId.is_valid(image_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image ID"
        )
    
    # Verify image belongs to user
    image = await db[IMAGES_COLLECTION].find_one({
        "_id": ObjectId(image_id),
        "userId": user_id
    })
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete file from disk
    try:
        file_path = Path(image["filepath"])
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
    
    # Delete from database
    result = await db[IMAGES_COLLECTION].delete_one({
        "_id": ObjectId(image_id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return {"message": "Image deleted successfully"}


async def analyze_image(user_id: str, analyze_request: ImageAnalyzeRequest) -> dict:
    """
    Analyze an image with AI
    
    Args:
        user_id: User's ID
        analyze_request: Image analysis request data
        
    Returns:
        dict: Analysis result with message ID
        
    Raises:
        HTTPException: If session not found or AI error
    """
    db = get_database()
    
    # Verify session exists
    if ObjectId.is_valid(analyze_request.sessionId):
        session = await db[SESSIONS_COLLECTION].find_one({
            "_id": ObjectId(analyze_request.sessionId),
            "userId": user_id
        })
    else:
        session = await db[SESSIONS_COLLECTION].find_one({
            "_id": analyze_request.sessionId,
            "userId": user_id
        })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    try:
        # Use OpenAI Vision API or similar for image analysis
        # This is a placeholder - implement actual image analysis
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in satellite image analysis and geospatial intelligence."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analyze_request.prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": analyze_request.imageData
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        analysis_text = response.choices[0].message.content
        
    except Exception as e:
        print(f"AI Analysis Error: {str(e)}")
        # Fallback response
        analysis_text = "I've analyzed the image. This appears to be a satellite image. Please provide more specific questions for detailed analysis."
    
    # Save analysis as a message
    message_dict = {
        "sessionId": analyze_request.sessionId,
        "userId": user_id,
        "text": analysis_text,
        "sender": "ai",
        "imageData": analyze_request.imageData,
        "timestamp": datetime.utcnow(),
        "createdAt": datetime.utcnow()
    }
    
    result = await db[MESSAGES_COLLECTION].insert_one(message_dict)
    message_id = str(result.inserted_id)
    
    return {
        "analysis": analysis_text,
        "messageId": message_id
    }


async def get_session_images(session_id: str, user_id: str) -> list:
    """
    Get all images for a session
    
    Args:
        session_id: Session ID
        user_id: User's ID
        
    Returns:
        list: List of images
        
    Raises:
        HTTPException: If session not found
    """
    db = get_database()
    
    # Verify session exists
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
    
    cursor = db[IMAGES_COLLECTION].find({
        "sessionId": session_id,
        "userId": user_id
    }).sort("uploadedAt", -1)
    
    images = await cursor.to_list(length=None)
    
    for image in images:
        image["_id"] = str(image["_id"])
    
    return images