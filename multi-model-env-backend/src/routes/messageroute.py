from fastapi import APIRouter, Depends
from src.modals.messagemodel import MessageCreate, MessageResponse, AIResponseRequest
from src.controllers import messagecontroller
from src.middleware.authmiddleware import get_current_user
from typing import List

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("", response_model=MessageResponse, status_code=201)
async def create_message_route(
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new message
    
    Protected Route - Requires JWT token
    
    Request Body:
        - sessionId: Session ID (required)
        - text: Message text (required)
        - imageData: Base64 image data (optional)
    
    Returns:
        Created message data
    """
    user_id = current_user["_id"]
    message = await messagecontroller.create_message(user_id, message_data)
    return message


@router.get("/{session_id}", response_model=List[MessageResponse])
async def get_messages_route(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all messages for a session
    
    Protected Route - Requires JWT token
    
    Parameters:
        - session_id: Session ID
    
    Returns:
        List of messages
    """
    user_id = current_user["_id"]
    messages = await messagecontroller.get_session_messages(session_id, user_id)
    return messages


@router.post("/ai-response", response_model=MessageResponse)
async def generate_ai_response_route(
    ai_request: AIResponseRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI response for a message
    
    Protected Route - Requires JWT token
    
    Request Body:
        - sessionId: Session ID (required)
        - messageId: Message ID to respond to (required)
    
    Returns:
        Generated AI message
    """
    user_id = current_user["_id"]
    ai_message = await messagecontroller.generate_ai_response(user_id, ai_request)
    return ai_message


@router.delete("/{message_id}")
async def delete_message_route(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a message
    
    Protected Route - Requires JWT token
    
    Parameters:
        - message_id: Message ID
    
    Returns:
        Success message
    """
    user_id = current_user["_id"]
    result = await messagecontroller.delete_message(message_id, user_id)
    return result