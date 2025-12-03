from fastapi import APIRouter, Depends, Response
from modals.usermodel import UserCreate, UserLogin, UpdateProfile
from controllers import authcontroller
from middleware.authmiddleware import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", status_code=201)
async def signup_route(user_data: UserCreate, response: Response):
    """
    Register a new user
    
    Request Body:
        - email: User's email
        - fullName: User's full name
        - password: User's password (min 6 characters)
    
    Returns:
        User data with JWT token set in cookie
    """
    user = await authcontroller.signup(user_data, response)
    return user

@router.post("/login")
async def login_route(user_data: UserLogin, response: Response):
    """
    Login user
    
    Request Body:
        - email: User's email
        - password: User's password
    
    Returns:
        User data with JWT token set in cookie
    """
    user = await authcontroller.login(user_data, response)
    return user

@router.post("/logout")
async def logout_route(response: Response):
    """
    Logout user by clearing JWT cookie
    
    Returns:
        Success message
    """
    result = await authcontroller.logout(response)
    return result

@router.get("/check")
async def check_auth_route(current_user: dict = Depends(get_current_user)):
    """
    Check if user is authenticated
    
    Protected Route - Requires JWT token
    
    Returns:
        Current user data
    """
    return current_user

@router.put("/update-profile")
async def update_profile_route(
    update_data: UpdateProfile,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user profile
    
    Protected Route - Requires JWT token
    
    Request Body:
        - fullName: User's full name (optional)
        - profilePic: User's profile picture URL (optional)
    
    Returns:
        Updated user data
    """
    user_id = current_user["_id"]
    updated_user = await authcontroller.update_profile(
        user_id,
        update_data.dict(exclude_unset=True)
    )
    return updated_user