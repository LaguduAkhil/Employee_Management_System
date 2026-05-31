"""Department service for department management."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models import Department
from app.repository import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.utils.exceptions import DepartmentNotFoundError, DepartmentAlreadyExistsError


class DepartmentService:
    """Service layer for department operations."""

    def __init__(self, db: Session):
        self.db = db
        self.dept_repo = DepartmentRepository(db)

    def create_department(
        self,
        dept_create: DepartmentCreate,
        created_by: int
    ) -> Department:
        """
        Create a new department.
        
        Args:
            dept_create: Department creation request
            created_by: ID of user creating the department
        
        Returns:
            Created department
        
        Raises:
            DepartmentAlreadyExistsError: If code already exists
        """
        existing = self.dept_repo.get_by_code(dept_create.code)
        if existing:
            raise DepartmentAlreadyExistsError(f"Department code {dept_create.code} already exists")
        
        dept_data = {
            **dept_create.dict(),
            "created_by": created_by,
            "updated_by": created_by
        }
        return self.dept_repo.create(dept_data)

    def get_department(self, dept_id: int) -> Department:
        """Get department by ID."""
        dept = self.dept_repo.get_by_id(dept_id)
        if not dept or dept.is_deleted:
            raise DepartmentNotFoundError(f"Department {dept_id} not found")
        return dept

    def list_departments(self, page: int = 1, page_size: int = 20) -> Tuple[List[Department], int]:
        """
        List all active departments with pagination.
        
        Returns:
            Tuple of (departments list, total count)
        """
        skip = (page - 1) * page_size
        depts = self.dept_repo.get_all_active(skip=skip, limit=page_size)
        total = self.dept_repo.count_active()
        return depts, total

    def search_departments(
        self,
        search_term: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Department], int]:
        """
        Search departments by name or code.
        
        Returns:
            Tuple of (departments list, total count)
        """
        skip = (page - 1) * page_size
        depts = self.dept_repo.search(search_term, skip=skip, limit=page_size)
        total = len(depts)  # Simple count for search results
        return depts, total

    def update_department(
        self,
        dept_id: int,
        dept_update: DepartmentUpdate,
        updated_by: int
    ) -> Department:
        """Update department details."""
        dept = self.get_department(dept_id)
        
        update_data = dept_update.dict(exclude_unset=True)
        update_data["updated_by"] = updated_by
        
        # Check if new code is unique
        if "code" in update_data and update_data["code"] != dept.code:
            existing = self.dept_repo.get_by_code(update_data["code"])
            if existing:
                raise DepartmentAlreadyExistsError(f"Department code {update_data['code']} already exists")
        
        return self.dept_repo.update(dept_id, update_data)

    def delete_department(self, dept_id: int) -> bool:
        """Soft delete a department."""
        dept = self.get_department(dept_id)
        return self.dept_repo.delete(dept_id)

    def get_department_by_code(self, code: str) -> Department:
        """Get department by code."""
        dept = self.dept_repo.get_by_code(code)
        if not dept:
            raise DepartmentNotFoundError(f"Department with code {code} not found")
        return dept
