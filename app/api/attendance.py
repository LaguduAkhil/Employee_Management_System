"""Attendance API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from app.db.database import get_db
from app.middleware.auth import get_current_user, require_role, require_roles
from app.models import User
from app.services.attendance_service import AttendanceService
from app.services.employee_service import EmployeeService
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse
)
from app.utils.exceptions import (
    AttendanceNotFoundError,
    InvalidInputError
)

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.post("", response_model=AttendanceResponse, status_code=201)
async def create_attendance(
    att_create: AttendanceCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Create an attendance record (Admin only).
    
    Marks attendance for an employee on a specific date.
    """
    att_service = AttendanceService(db)
    
    try:
        att = att_service.create_attendance(att_create)
        return AttendanceResponse.from_orm(att)
    except InvalidInputError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/{att_id}", response_model=AttendanceResponse)
async def get_attendance(
    att_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance record by ID."""
    att_service = AttendanceService(db)
    
    try:
        att = att_service.get_attendance(att_id)
        return AttendanceResponse.from_orm(att)
    except AttendanceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/employee/{emp_id}", response_model=dict)
async def get_employee_attendance(
    emp_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get attendance records for an employee.
    
    Employee can view own, Manager can view team, Admin can view all.
    """
    att_service = AttendanceService(db)
    emp_service = EmployeeService(db)
    
    try:
        # Authorization check
        if current_user.role.value == "employee":
            emp = emp_service.get_employee_by_user_id(current_user.id)
            if emp.id != emp_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view other's attendance")
        
        records, total = att_service.list_attendance_by_employee(emp_id, page, page_size)
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [AttendanceResponse.from_orm(r) for r in records]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/employee/{emp_id}/month", response_model=dict)
async def get_employee_monthly_attendance(
    emp_id: int,
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get attendance summary for an employee for a specific month.
    """
    att_service = AttendanceService(db)
    emp_service = EmployeeService(db)
    
    try:
        # Authorization check
        if current_user.role.value == "employee":
            emp = emp_service.get_employee_by_user_id(current_user.id)
            if emp.id != emp_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view other's attendance")
        
        summary = att_service.get_attendance_summary(emp_id, year, month)
        
        return {
            "employee_id": emp_id,
            "year": year,
            "month": month,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/employee/{emp_id}/range", response_model=dict)
async def get_employee_attendance_range(
    emp_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get attendance records for an employee in a date range.
    """
    att_service = AttendanceService(db)
    emp_service = EmployeeService(db)
    
    try:
        # Authorization check
        if current_user.role.value == "employee":
            emp = emp_service.get_employee_by_user_id(current_user.id)
            if emp.id != emp_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view other's attendance")
        
        records = att_service.list_attendance_by_date_range(emp_id, start_date, end_date)
        
        return {
            "employee_id": emp_id,
            "start_date": start_date,
            "end_date": end_date,
            "count": len(records),
            "data": [AttendanceResponse.from_orm(r) for r in records]
        }
    except InvalidInputError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put("/{att_id}", response_model=AttendanceResponse)
async def update_attendance(
    att_id: int,
    att_update: AttendanceUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update attendance record (Admin only)."""
    att_service = AttendanceService(db)
    
    try:
        att = att_service.update_attendance(att_id, att_update, current_user.id)
        return AttendanceResponse.from_orm(att)
    except AttendanceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{att_id}", status_code=204)
async def delete_attendance(
    att_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Soft delete attendance record (Admin only)."""
    att_service = AttendanceService(db)
    
    try:
        att_service.delete_attendance(att_id)
    except AttendanceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
