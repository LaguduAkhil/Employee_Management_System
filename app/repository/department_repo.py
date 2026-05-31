"""Department repository."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import Department
from app.repository.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """Repository for Department model."""

    def __init__(self, db: Session):
        super().__init__(db, Department)

    def get_by_code(self, code: str) -> Optional[Department]:
        """Get department by code."""
        return self.db.query(Department).filter(
            Department.code == code,
            Department.is_deleted == False
        ).first()

    def get_by_name(self, name: str) -> Optional[Department]:
        """Get department by name."""
        return self.db.query(Department).filter(
            Department.name == name,
            Department.is_deleted == False
        ).first()

    def get_all_active(self, skip: int = 0, limit: int = 100) -> List[Department]:
        """Get all active departments."""
        return self.db.query(Department).filter(
            Department.is_deleted == False
        ).offset(skip).limit(limit).all()

    def search(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Department]:
        """Search departments by name or code."""
        return self.db.query(Department).filter(
            Department.is_deleted == False,
            (Department.name.ilike(f"%{search_term}%") | Department.code.ilike(f"%{search_term}%"))
        ).offset(skip).limit(limit).all()

    def count_active(self) -> int:
        """Count active departments."""
        from sqlalchemy import func
        return self.db.query(func.count(Department.id)).filter(
            Department.is_deleted == False
        ).scalar()
