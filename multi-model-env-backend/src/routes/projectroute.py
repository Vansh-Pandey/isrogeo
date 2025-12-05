from fastapi import APIRouter, Depends
from src.modals.projectmodel import ProjectCreate, ProjectUpdate, ProjectResponse
from src.modals.sessionmodel import SessionResponse
from src.controllers import projectcontroller
from src.middleware.authmiddleware import get_current_user
from typing import List

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project_route(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new project
    
    Protected Route - Requires JWT token
    
    Request Body:
        - name: Project name (required)
        - description: Project description (optional)
        - color: Project color hex code (optional, default: "#6366f1")
    
    Returns:
        Created project data
    """
    user_id = current_user["_id"]
    project = await projectcontroller.create_project(user_id, project_data)
    return project


@router.get("", response_model=List[ProjectResponse])
async def get_projects_route(current_user: dict = Depends(get_current_user)):
    """
    Get all projects for current user
    
    Protected Route - Requires JWT token
    
    Returns:
        List of projects
    """
    user_id = current_user["_id"]
    projects = await projectcontroller.get_user_projects(user_id)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_route(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific project by ID
    
    Protected Route - Requires JWT token
    
    Parameters:
        - project_id: Project ID
    
    Returns:
        Project data
    """
    user_id = current_user["_id"]
    project = await projectcontroller.get_project_by_id(project_id, user_id)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_route(
    project_id: str,
    update_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a project
    
    Protected Route - Requires JWT token
    
    Parameters:
        - project_id: Project ID
    
    Request Body:
        - name: Project name (optional)
        - description: Project description (optional)
        - color: Project color hex code (optional)
    
    Returns:
        Updated project data
    """
    user_id = current_user["_id"]
    updated_project = await projectcontroller.update_project(
        project_id,
        user_id,
        update_data
    )
    return updated_project


@router.delete("/{project_id}")
async def delete_project_route(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a project
    
    Protected Route - Requires JWT token
    
    Parameters:
        - project_id: Project ID
    
    Returns:
        Success message
    """
    user_id = current_user["_id"]
    result = await projectcontroller.delete_project(project_id, user_id)
    return result


@router.get("/{project_id}/sessions", response_model=List[SessionResponse])
async def get_project_sessions_route(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all sessions in a project
    
    Protected Route - Requires JWT token
    
    Parameters:
        - project_id: Project ID
    
    Returns:
        List of sessions in the project
    """
    user_id = current_user["_id"]
    sessions = await projectcontroller.get_project_sessions(project_id, user_id)
    return sessions