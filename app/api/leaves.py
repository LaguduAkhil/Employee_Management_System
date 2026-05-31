"""Leave API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user, require_role, require_roles
from app.models import User
from app.services.leave_service import LeaveService
from app.services.employee_service import EmployeeService
from app.schemas.leave import (
    LeaveCreate,
    LeaveUpdate,
    LeaveResponse,
    LeaveListResponse
)
from app.core.enums import LeaveStatusEnum
from app.utils.exceptions import (
    LeaveNotFoundError,
    InvalidInputError
)

router = APIRouter(prefix="/api/leaves", tags=["Leaves"])


@router.post("", response_model=LeaveResponse, status_code=201)
async def create_leave_request(
    leave_create: LeaveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new leave request.
    
    Employee submits leave request. Employees can only create for themselves.
    """
    leave_service = LeaveService(db)
    emp_service = EmployeeService(db)
    
    try:
        # Get current employee
        emp = emp_service.get_employee_by_user_id(current_user.id)
        leave = leave_service.create_leave_request(emp.id, leave_create)
        return LeaveResponse.from_orm(leave)
    except InvalidInputError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{leave_id}", response_model=LeaveResponse)
async def get_leave(
    leave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leave request by ID."""
    leave_service = LeaveService(db)
    emp_service = EmployeeService(db)
    
    try:
        leave = leave_service.get_leave(leave_id)
        
        # Authorization: employee can view own, manager/admin can view team/all
        if current_user.role.value == "employee":
            emp = emp_service.get_employee_by_user_id(current_user.id)
            if leave.employee_id != emp.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view other's leave request")
        
        return LeaveResponse.from_orm(leave)
    except LeaveNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("", response_model=LeaveListResponse)
async def list_leaves(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List leave requests.
    
    Admin/Manager see all pending, Employee sees their own.
    """
    leave_service = LeaveService(db)
    emp_service = EmployeeService(db)
    
    try:
        if current_user.role.value == "admin":
            if status_filter:
                status_enum = LeaveStatusEnum(status_filter)
                leaves, total = leave_service.list_pending_leaves(page, page_size) if status_filter == "pending" else ([], 0)
            else:
                leaves, total = leave_service.list_pending_leaves(page, page_size)
        elif current_user.role.value == "manager":
            leaves, total = leave_service.list_pending_leaves(page, page_size)
        else:
            # Employee sees their own
            emp = emp_service.get_employee_by_user_id(current_user.id)
            leaves, total = leave_service.list_leaves_by_employee(emp.id, page, page_size)
        
        return LeaveListResponse(
            total=total,
            page=page,
            page_size=page_size,
            data=[LeaveResponse.from_orm(l) for l in leaves]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{leave_id}/approve", response_model=LeaveResponse)
async def approve_leave(
    leave_id: int,
    remarks: str = Query(None),
    current_user: User = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db)
):
    """
    Approve a leave request (Admin/Manager only).
    """
    leave_service = LeaveService(db)
    
    try:
        leave = leave_service.approve_leave(leave_id, current_user.id, remarks)
        return LeaveResponse.from_orm(leave)
    except LeaveNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except InvalidInputError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/{leave_id}/reject", response_model=LeaveResponse)
async def reject_leave(
    leave_id: int,
    remarks: str = Query(...),
    current_user: User = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db)
):
    """
    Reject a leave request (Admin/Manager only).
    """
    leave_service = LeaveService(db)
    
    try:
        leave = leave_service.reject_leave(leave_id, current_user.id, remarks)
        return LeaveResponse.from_orm(leave)
    except LeaveNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except InvalidInputError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/{leave_id}/cancel", response_model=LeaveResponse)
async def cancel_leave(
    leave_id: int,
    remarks: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a leave request (Employee cancels their own, Admin/Manager can cancel any).
    """
    leave_service = LeaveService(db)
    emp_service = EmployeeService(db)
    
    try:
        leave = leave_service.get_leave(leave_id)
        
        # Authorization check
        if current_user.role.value == "employee":
            emp = emp_service.get_employee_by_user_id(current_user.id)
            if leave.employee_id != emp.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only cancel your own leave")
        
        leave = leave_service.cancel_leave(leave_id, remarks)
        return LeaveResponse.from_orm(leave)
    except LeaveNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except InvalidInputError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.delete("/{leave_id}", status_code=204)
async def delete_leave(
    leave_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Hard delete leave request (Admin only)."""
    leave_service = LeaveService(db)
    
    try:
        leave_service.get_leave(leave_id)
        leave_service.leave_repo.hard_delete(leave_id)
    except LeaveNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
