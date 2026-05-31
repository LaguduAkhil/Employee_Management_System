"""Employee API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user, require_role, require_roles
from app.models import User
from app.services.employee_service import EmployeeService
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse
)
from app.utils.exceptions import (
    EmployeeNotFoundError,
    EmployeeAlreadyExistsError,
    InvalidInputError
)

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    emp_create: EmployeeCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Create a new employee (Admin only).
    
    Creates both user account and employee record.
    """
    emp_service = EmployeeService(db)
    
    try:
        emp = emp_service.create_employee(emp_create, current_user.id)
        return EmployeeResponse.from_orm(emp)
    except (EmployeeAlreadyExistsError, InvalidInputError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/me", response_model=EmployeeResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current logged-in employee profile.
    
    Employees and managers can view their own profile.
    """
    emp_service = EmployeeService(db)
    
    try:
        emp = emp_service.get_employee_by_user_id(current_user.id)
        return EmployeeResponse.from_orm(emp)
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/{emp_id}", response_model=EmployeeResponse)
async def get_employee(
    emp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employee by ID."""
    emp_service = EmployeeService(db)
    
    try:
        emp = emp_service.get_employee(emp_id)
        
        # Authorization check: employee can only view own, manager can view team
        if current_user.role.value == "employee" and emp.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view other employee's profile")
        
        return EmployeeResponse.from_orm(emp)
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all employees with pagination.
    
    Admin sees all employees, Manager sees their team, Employee sees only themselves.
    """
    emp_service = EmployeeService(db)
    
    if current_user.role.value == "admin":
        emps, total = emp_service.list_employees(page, page_size)
    elif current_user.role.value == "manager":
        emps, total = emp_service.get_manager_team(current_user.id, page, page_size)
    else:
        # Employee can only see their own profile
        try:
            emp = emp_service.get_employee_by_user_id(current_user.id)
            return EmployeeListResponse(
                total=1,
                page=page,
                page_size=page_size,
                data=[EmployeeResponse.from_orm(emp)]
            )
        except EmployeeNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    return EmployeeListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=[EmployeeResponse.from_orm(e) for e in emps]
    )


@router.get("/search/{search_term}", response_model=EmployeeListResponse)
async def search_employees(
    search_term: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Search employees by name, email, code."""
    emp_service = EmployeeService(db)
    emps, total = emp_service.search_employees(search_term, page, page_size)
    
    return EmployeeListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=[EmployeeResponse.from_orm(e) for e in emps]
    )


@router.put("/{emp_id}", response_model=EmployeeResponse)
async def update_employee(
    emp_id: int,
    emp_update: EmployeeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update employee details.
    
    Admin can update any employee, Managers can update their team, Employees can update themselves.
    """
    emp_service = EmployeeService(db)
    
    try:
        # Authorization check
        emp = emp_service.get_employee(emp_id)
        if current_user.role.value == "employee" and emp.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update other employee")
        elif current_user.role.value == "manager" and emp.department_id != emp_service.get_employee_by_user_id(current_user.id).department_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only update employees in your department")
        
        emp = emp_service.update_employee(emp_id, emp_update, current_user.id)
        return EmployeeResponse.from_orm(emp)
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except InvalidInputError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.delete("/{emp_id}", status_code=204)
async def delete_employee(
    emp_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Soft delete employee (Admin only)."""
    emp_service = EmployeeService(db)
    
    try:
        emp_service.delete_employee(emp_id)
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
