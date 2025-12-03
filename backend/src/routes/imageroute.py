from fastapi import APIRouter, Depends, UploadFile, File, Form
from modals.imagemodel import ImageResponse, ImageAnalyzeRequest, ImageAnalyzeResponse
from controllers import imagecontroller
from middleware.authmiddleware import get_current_user
from typing import List

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/upload", response_model=ImageResponse, status_code=201)
async def upload_image_route(
    image: UploadFile = File(...),
    sessionId: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload an image
    
    Protected Route - Requires JWT token
    
    Form Data:
        - image: Image file (JPEG or PNG)
        - sessionId: Session ID
    
    Returns:
        Uploaded image data
    """
    user_id = current_user["_id"]
    uploaded_image = await imagecontroller.upload_image(user_id, sessionId, image)
    return uploaded_image


@router.delete("/{image_id}")
async def delete_image_route(
    image_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an image
    
    Protected Route - Requires JWT token
    
    Parameters:
        - image_id: Image ID
    
    Returns:
        Success message
    """
    user_id = current_user["_id"]
    result = await imagecontroller.delete_image(image_id, user_id)
    return result


@router.post("/analyze", response_model=ImageAnalyzeResponse)
async def analyze_image_route(
    analyze_request: ImageAnalyzeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze an image with AI
    
    Protected Route - Requires JWT token
    
    Request Body:
        - sessionId: Session ID (required)
        - imageData: Base64 image data (required)
        - prompt: Analysis prompt (required)
    
    Returns:
        Analysis result with message ID
    """
    user_id = current_user["_id"]
    result = await imagecontroller.analyze_image(user_id, analyze_request)
    return result


@router.get("/session/{session_id}", response_model=List[ImageResponse])
async def get_session_images_route(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all images for a session
    
    Protected Route - Requires JWT token
    
    Parameters:
        - session_id: Session ID
    
    Returns:
        List of images
    """
    user_id = current_user["_id"]
    images = await imagecontroller.get_session_images(session_id, user_id)
    return images