"""Employee repository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Employee
from app.repository.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    """Repository for Employee model."""

    def __init__(self, db: Session):
        super().__init__(db, Employee)

    def get_by_employee_code(self, code: str) -> Optional[Employee]:
        """Get employee by employee code."""
        return self.db.query(Employee).filter(
            Employee.employee_code == code,
            Employee.is_deleted == False
        ).first()

    def get_by_user_id(self, user_id: int) -> Optional[Employee]:
        """Get employee by user ID."""
        return self.db.query(Employee).filter(
            Employee.user_id == user_id,
            Employee.is_deleted == False
        ).first()

    def get_by_department(self, department_id: int, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Get all employees in a department."""
        return self.db.query(Employee).filter(
            Employee.department_id == department_id,
            Employee.is_deleted == False
        ).offset(skip).limit(limit).all()

    def get_all_active(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Get all active employees."""
        return self.db.query(Employee).filter(
            Employee.is_deleted == False
        ).offset(skip).limit(limit).all()

    def search(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Search employees by name, email, code, or department.
        """
        from app.models import User
        return self.db.query(Employee).join(User).filter(
            Employee.is_deleted == False,
            (Employee.first_name.ilike(f"%{search_term}%") |
             Employee.last_name.ilike(f"%{search_term}%") |
             Employee.employee_code.ilike(f"%{search_term}%") |
             User.email.ilike(f"%{search_term}%"))
        ).offset(skip).limit(limit).all()

    def count_by_department(self, department_id: int) -> int:
        """Count employees in a department."""
        return self.db.query(func.count(Employee.id)).filter(
            Employee.department_id == department_id,
            Employee.is_deleted == False
        ).scalar()

    def count_active(self) -> int:
        """Count active employees."""
        return self.db.query(func.count(Employee.id)).filter(
            Employee.is_deleted == False
        ).scalar()
