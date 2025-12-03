from fastapi import APIRouter, Depends
from modals.sessionmodel import SessionCreate, SessionUpdate, ShareSessionResponse
from controllers import sessioncontroller
from middleware.authmiddleware import get_current_user
from typing import List

router = APIRouter(prefix="/sessions", tags=["Sessions"])

def serialize_session(session):
    return {
        "id": str(session._id),
        "title": session.title,
        "type": session.type,
        "project_id": str(session.project_id) if session.project_id else None,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
    }

@router.post("", status_code=201)
async def create_session_route(
    session_data: SessionCreate,
    current_user: dict = Depends(get_current_user)
):
     
    user_id = current_user["_id"]
    session = await sessioncontroller.create_session(user_id, session_data)
    
    # Ensure _id is present
    if session and "_id" not in session:
        print("⚠️ WARNING: Session missing _id after creation!")
    
    return serialize_session(session)



@router.get("")
async def get_sessions_route(current_user: dict = Depends(get_current_user)):
     
    user_id = current_user["_id"]
    sessions = await sessioncontroller.get_user_sessions(user_id)
    
    # Debug: Check if sessions have _id
    for session in sessions:
        if "_id" not in session:
            print(f"⚠️ WARNING: Session missing _id: {session}")
    
    return sessions


@router.get("/{session_id}")
async def get_session_route(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    
    user_id = current_user["_id"]
    session = await sessioncontroller.get_session_by_id(session_id, user_id)
    return session


@router.put("/{session_id}")
async def update_session_route(
    session_id: str,
    update_data: SessionUpdate,
    current_user: dict = Depends(get_current_user)
):
     
    user_id = current_user["_id"]
    updated_session = await sessioncontroller.update_session(
        session_id,
        user_id,
        update_data
    )
    return updated_session


@router.delete("/{session_id}")
async def delete_session_route(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
   
    user_id = current_user["_id"]
    result = await sessioncontroller.delete_session(session_id, user_id)
    return result


@router.post("/{session_id}/share", response_model=ShareSessionResponse)
async def share_session_route(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
     
    user_id = current_user["_id"]
    result = await sessioncontroller.share_session(session_id, user_id)
    return result