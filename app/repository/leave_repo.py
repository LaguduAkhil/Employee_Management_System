"""Leave repository."""

from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Leave
from app.core.enums import LeaveStatusEnum
from app.repository.base import BaseRepository


class LeaveRepository(BaseRepository[Leave]):
    """Repository for Leave model."""

    def __init__(self, db: Session):
        super().__init__(db, Leave)

    def get_by_employee(self, employee_id: int, skip: int = 0, limit: int = 100) -> List[Leave]:
        """Get all leaves for an employee."""
        return self.db.query(Leave).filter(
            Leave.employee_id == employee_id
        ).offset(skip).limit(limit).all()

    def get_by_employee_and_status(
        self,
        employee_id: int,
        status: LeaveStatusEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[Leave]:
        """Get leaves for an employee with specific status."""
        return self.db.query(Leave).filter(
            Leave.employee_id == employee_id,
            Leave.status == status
        ).offset(skip).limit(limit).all()

    def get_pending_leaves(self, skip: int = 0, limit: int = 100) -> List[Leave]:
        """Get all pending leave requests."""
        return self.db.query(Leave).filter(
            Leave.status == LeaveStatusEnum.PENDING
        ).offset(skip).limit(limit).all()

    def get_by_date_range(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Leave]:
        """Get leaves in a date range for an employee."""
        return self.db.query(Leave).filter(
            Leave.employee_id == employee_id,
            Leave.start_date >= start_date,
            Leave.end_date <= end_date
        ).all()

    def count_by_employee_and_status(
        self,
        employee_id: int,
        status: LeaveStatusEnum
    ) -> int:
        """Count leaves for an employee with specific status."""
        return self.db.query(func.count(Leave.id)).filter(
            Leave.employee_id == employee_id,
            Leave.status == status
        ).scalar()

    def count_pending(self) -> int:
        """Count all pending leave requests."""
        return self.db.query(func.count(Leave.id)).filter(
            Leave.status == LeaveStatusEnum.PENDING
        ).scalar()
