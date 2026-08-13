from fastapi import APIRouter, Depends, HTTPException, Query, status
from mysql.connector import MySQLConnection
from typing import Any, List, Optional

from ...schemas.admin import BranchCreate, BranchResponse, BranchUpdate
from ...models import branch as branch_model
from ...core.database import get_db
from ...api.dependencies import get_current_active_manager, get_current_user

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("", response_model=List[BranchResponse])
def get_branches(
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """List all active branches."""
    return branch_model.get_all_branches(conn)


@router.post("", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(
    branch: BranchCreate,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Create a new branch location."""
    branch_id = branch_model.create_branch(
        conn,
        name=branch.name,
        address=branch.address,
        phone=branch.phone,
        email=branch.email,
        created_by=current_user["id"],
    )
    return branch_model.get_branch_by_id(conn, branch_id)


@router.get("/{branch_id}", response_model=BranchResponse)
def get_branch(
    branch_id: int,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Get a specific branch by ID."""
    branch = branch_model.get_branch_by_id(conn, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@router.put("/{branch_id}", response_model=BranchResponse)
def update_branch(
    branch_id: int,
    branch: BranchUpdate,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Update an existing branch."""
    success = branch_model.update_branch(conn, branch_id, branch.model_dump(exclude_unset=True))
    if not success:
        raise HTTPException(status_code=404, detail="Branch not found or no changes")
    return branch_model.get_branch_by_id(conn, branch_id)


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_branch(
    branch_id: int,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Deactivate a branch (soft delete)."""
    success = branch_model.delete_branch(conn, branch_id)
    if not success:
        raise HTTPException(status_code=404, detail="Branch not found")
    return None


@router.post("/{branch_id}/assign-user/{user_id}", status_code=status.HTTP_201_CREATED)
def assign_user_to_branch(
    branch_id: int,
    user_id: int,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Assign a user to a specific branch."""
    branch = branch_model.get_branch_by_id(conn, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    branch_model.assign_branch_to_user(conn, user_id, branch_id)
    return {"message": f"User {user_id} assigned to branch {branch_id}"}


@router.get("/{branch_id}/user", response_model=Any)
def get_branch_user(
    branch_id: int,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get the branch assigned to the current user."""
    return branch_model.get_user_branch(conn, current_user["id"])