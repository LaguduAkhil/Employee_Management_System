"""Employee service for employee management."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models import Employee, User, Department
from app.repository import EmployeeRepository, UserRepository, DepartmentRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.core.security import hash_password
from app.core.enums import RoleEnum
from app.utils.exceptions import (
    EmployeeNotFoundError,
    EmployeeAlreadyExistsError,
    InvalidInputError
)


class EmployeeService:
    """Service layer for employee operations."""

    def __init__(self, db: Session):
        self.db = db
        self.emp_repo = EmployeeRepository(db)
        self.user_repo = UserRepository(db)
        self.dept_repo = DepartmentRepository(db)

    def create_employee(
        self,
        emp_create: EmployeeCreate,
        created_by: int
    ) -> Employee:
        """
        Create a new employee and associated user account.
        
        Args:
            emp_create: Employee creation request
            created_by: ID of user creating the employee
        
        Returns:
            Created employee
        
        Raises:
            EmployeeAlreadyExistsError: If email or code already exists
            InvalidInputError: If department doesn't exist
        """
        # Validate department exists
        dept = self.dept_repo.get_by_id(emp_create.department_id)
        if not dept or dept.is_deleted:
            raise InvalidInputError(f"Department {emp_create.department_id} not found")

        # Check if employee code exists
        existing_emp = self.emp_repo.get_by_employee_code(emp_create.employee_code)
        if existing_emp:
            raise EmployeeAlreadyExistsError(f"Employee code {emp_create.employee_code} already exists")

        # Check if email exists
        existing_user = self.user_repo.get_by_email(emp_create.email)
        if existing_user:
            raise EmployeeAlreadyExistsError(f"Email {emp_create.email} already registered")

        # Create user account
        user = self.user_repo.create_user(
            email=emp_create.email,
            password_hash=hash_password(emp_create.password),
            role=RoleEnum.EMPLOYEE
        )

        # Create employee record
        emp_data = {
            "user_id": user.id,
            "employee_code": emp_create.employee_code,
            "first_name": emp_create.first_name,
            "last_name": emp_create.last_name,
            "phone": emp_create.phone,
            "date_of_birth": emp_create.date_of_birth,
            "date_of_joining": emp_create.date_of_joining,
            "department_id": emp_create.department_id,
            "created_by": created_by,
            "updated_by": created_by
        }
        return self.emp_repo.create(emp_data)

    def get_employee(self, emp_id: int) -> Employee:
        """Get employee by ID."""
        emp = self.emp_repo.get_by_id(emp_id)
        if not emp or emp.is_deleted:
            raise EmployeeNotFoundError(f"Employee {emp_id} not found")
        return emp

    def get_employee_by_user_id(self, user_id: int) -> Employee:
        """Get employee by user ID."""
        emp = self.emp_repo.get_by_user_id(user_id)
        if not emp or emp.is_deleted:
            raise EmployeeNotFoundError(f"Employee for user {user_id} not found")
        return emp

    def list_employees(self, page: int = 1, page_size: int = 20) -> Tuple[List[Employee], int]:
        """List all active employees with pagination."""
        skip = (page - 1) * page_size
        emps = self.emp_repo.get_all_active(skip=skip, limit=page_size)
        total = self.emp_repo.count_active()
        return emps, total

    def list_by_department(
        self,
        dept_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Employee], int]:
        """List employees in a department."""
        skip = (page - 1) * page_size
        emps = self.emp_repo.get_by_department(dept_id, skip=skip, limit=page_size)
        total = self.emp_repo.count_by_department(dept_id)
        return emps, total

    def search_employees(
        self,
        search_term: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Employee], int]:
        """Search employees by name, email, code, or department."""
        skip = (page - 1) * page_size
        emps = self.emp_repo.search(search_term, skip=skip, limit=page_size)
        total = len(emps)  # Simple count for search results
        return emps, total

    def update_employee(
        self,
        emp_id: int,
        emp_update: EmployeeUpdate,
        updated_by: int
    ) -> Employee:
        """Update employee details."""
        emp = self.get_employee(emp_id)
        
        # Validate department if being changed
        if emp_update.department_id:
            dept = self.dept_repo.get_by_id(emp_update.department_id)
            if not dept or dept.is_deleted:
                raise InvalidInputError(f"Department {emp_update.department_id} not found")

        update_data = emp_update.dict(exclude_unset=True)
        update_data["updated_by"] = updated_by
        
        return self.emp_repo.update(emp_id, update_data)

    def delete_employee(self, emp_id: int) -> bool:
        """Soft delete an employee."""
        emp = self.get_employee(emp_id)
        return self.emp_repo.delete(emp_id)

    def get_manager_team(
        self,
        manager_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Employee], int]:
        """Get all employees under a manager's department."""
        manager_emp = self.get_employee_by_user_id(manager_id)
        return self.list_by_department(manager_emp.department_id, page, page_size)
