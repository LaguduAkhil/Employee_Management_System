"""Department API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models import User
from app.services.department_service import DepartmentService
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.utils.exceptions import DepartmentNotFoundError, DepartmentAlreadyExistsError

router = APIRouter(prefix="/api/departments", tags=["Departments"])


@router.post("", response_model=DepartmentResponse, status_code=201)
async def create_department(
    dept_create: DepartmentCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Create a new department (Admin only).
    
    Args:
        dept_create: Department creation data
    
    Returns:
        Created department
    """
    dept_service = DepartmentService(db)
    
    try:
        dept = dept_service.create_department(dept_create, current_user.id)
        return DepartmentResponse.from_orm(dept)
    except DepartmentAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.get("/{dept_id}", response_model=DepartmentResponse)
async def get_department(
    dept_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get department by ID."""
    dept_service = DepartmentService(db)
    
    try:
        dept = dept_service.get_department(dept_id)
        return DepartmentResponse.from_orm(dept)
    except DepartmentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("", response_model=dict)
async def list_departments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all departments with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        Paginated list of departments
    """
    dept_service = DepartmentService(db)
    depts, total = dept_service.list_departments(page, page_size)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [DepartmentResponse.from_orm(d) for d in depts]
    }


@router.get("/search/{search_term}", response_model=dict)
async def search_departments(
    search_term: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search departments by name or code."""
    dept_service = DepartmentService(db)
    depts, total = dept_service.search_departments(search_term, page, page_size)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [DepartmentResponse.from_orm(d) for d in depts]
    }


@router.put("/{dept_id}", response_model=DepartmentResponse)
async def update_department(
    dept_id: int,
    dept_update: DepartmentUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update department (Admin only)."""
    dept_service = DepartmentService(db)
    
    try:
        dept = dept_service.update_department(dept_id, dept_update, current_user.id)
        return DepartmentResponse.from_orm(dept)
    except DepartmentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DepartmentAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.delete("/{dept_id}", status_code=204)
async def delete_department(
    dept_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Soft delete department (Admin only)."""
    dept_service = DepartmentService(db)
    
    try:
        dept_service.delete_department(dept_id)
    except DepartmentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
