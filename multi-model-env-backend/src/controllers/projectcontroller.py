from fastapi import HTTPException, status
from src.modals.projectmodel import ProjectCreate, ProjectUpdate
from src.lib.db import get_database, PROJECTS_COLLECTION, SESSIONS_COLLECTION
from bson import ObjectId
from datetime import datetime


async def create_project(user_id: str, project_data: ProjectCreate) -> dict:
    """
    Create a new project
    
    Args:
        user_id: User's ID
        project_data: Project creation data
        
    Returns:
        dict: Created project data
    """
    db = get_database()
    
    project_dict = {
        "userId": user_id,
        "name": project_data.name,
        "description": project_data.description,
        "color": project_data.color,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db[PROJECTS_COLLECTION].insert_one(project_dict)
    
    created_project = await db[PROJECTS_COLLECTION].find_one({"_id": result.inserted_id})
    created_project["_id"] = str(created_project["_id"])
    
    return created_project


async def get_user_projects(user_id: str) -> list:
    """
    Get all projects for a user
    
    Args:
        user_id: User's ID
        
    Returns:
        list: List of projects
    """
    db = get_database()
    
    cursor = db[PROJECTS_COLLECTION].find({"userId": user_id}).sort("createdAt", -1)
    projects = await cursor.to_list(length=None)
    
    for project in projects:
        project["_id"] = str(project["_id"])
    
    return projects


async def get_project_by_id(project_id: str, user_id: str) -> dict:
    """
    Get a specific project by ID
    
    Args:
        project_id: Project ID
        user_id: User's ID
        
    Returns:
        dict: Project data
        
    Raises:
        HTTPException: If project not found or unauthorized
    """
    db = get_database()
    
    if not ObjectId.is_valid(project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID"
        )
    
    project = await db[PROJECTS_COLLECTION].find_one({
        "_id": ObjectId(project_id),
        "userId": user_id
    })
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project["_id"] = str(project["_id"])
    return project


async def update_project(project_id: str, user_id: str, update_data: ProjectUpdate) -> dict:
    """
    Update a project
    
    Args:
        project_id: Project ID
        user_id: User's ID
        update_data: Data to update
        
    Returns:
        dict: Updated project data
        
    Raises:
        HTTPException: If project not found or no data to update
    """
    db = get_database()
    
    if not ObjectId.is_valid(project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID"
        )
    
    update_dict = update_data.dict(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    update_dict["updatedAt"] = datetime.utcnow()
    
    result = await db[PROJECTS_COLLECTION].find_one_and_update(
        {"_id": ObjectId(project_id), "userId": user_id},
        {"$set": update_dict},
        return_document=True
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    result["_id"] = str(result["_id"])
    return result


async def delete_project(project_id: str, user_id: str) -> dict:
    """
    Delete a project
    
    Args:
        project_id: Project ID
        user_id: User's ID
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If project not found
    """
    db = get_database()
    
    if not ObjectId.is_valid(project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID"
        )
    
    result = await db[PROJECTS_COLLECTION].delete_one({
        "_id": ObjectId(project_id),
        "userId": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Remove projectId from all sessions
    await db[SESSIONS_COLLECTION].update_many(
        {"projectId": project_id},
        {"$set": {"projectId": None}}
    )
    
    return {"message": "Project deleted successfully"}


async def get_project_sessions(project_id: str, user_id: str) -> list:
    """
    Get all sessions in a project
    
    Args:
        project_id: Project ID
        user_id: User's ID
        
    Returns:
        list: List of sessions in the project
        
    Raises:
        HTTPException: If project not found
    """
    db = get_database()
    
    if not ObjectId.is_valid(project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID"
        )
    
    # Verify project belongs to user
    project = await db[PROJECTS_COLLECTION].find_one({
        "_id": ObjectId(project_id),
        "userId": user_id
    })
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    cursor = db[SESSIONS_COLLECTION].find({
        "projectId": project_id,
        "userId": user_id
    }).sort("updatedAt", -1)
    
    sessions = await cursor.to_list(length=None)
    
    for session in sessions:
        session["_id"] = str(session["_id"])
    
    return sessions