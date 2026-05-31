"""Attendance service for attendance management."""

from typing import List, Tuple
from datetime import date
from sqlalchemy.orm import Session

from app.models import Attendance
from app.repository import AttendanceRepository, EmployeeRepository
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate
from app.utils.exceptions import AttendanceNotFoundError, InvalidInputError


class AttendanceService:
    """Service layer for attendance operations."""

    def __init__(self, db: Session):
        self.db = db
        self.att_repo = AttendanceRepository(db)
        self.emp_repo = EmployeeRepository(db)

    def create_attendance(self, att_create: AttendanceCreate) -> Attendance:
        """
        Create an attendance record.
        
        Args:
            att_create: Attendance creation request
        
        Returns:
            Created attendance record
        
        Raises:
            InvalidInputError: If employee not found or duplicate record
        """
        emp = self.emp_repo.get_by_id(att_create.employee_id)
        if not emp or emp.is_deleted:
            raise InvalidInputError(f"Employee {att_create.employee_id} not found")

        # Check if attendance already exists for date
        existing = self.att_repo.get_by_employee_and_date(
            att_create.employee_id,
            att_create.attendance_date
        )
        if existing:
            raise InvalidInputError(
                f"Attendance already recorded for employee {att_create.employee_id} on {att_create.attendance_date}"
            )

        att_data = att_create.dict()
        return self.att_repo.create(att_data)

    def get_attendance(self, att_id: int) -> Attendance:
        """Get attendance record by ID."""
        att = self.att_repo.get_by_id(att_id)
        if not att:
            raise AttendanceNotFoundError(f"Attendance record {att_id} not found")
        return att

    def get_attendance_by_employee_and_date(
        self,
        emp_id: int,
        att_date: date
    ) -> Attendance:
        """Get attendance record for specific employee and date."""
        att = self.att_repo.get_by_employee_and_date(emp_id, att_date)
        if not att:
            raise AttendanceNotFoundError(
                f"No attendance record for employee {emp_id} on {att_date}"
            )
        return att

    def list_attendance_by_employee(
        self,
        emp_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Attendance], int]:
        """List all attendance records for an employee."""
        skip = (page - 1) * page_size
        records = self.att_repo.get_by_employee(emp_id, skip=skip, limit=page_size)
        total = len(records)  # Can be optimized
        return records, total

    def list_attendance_by_employee_and_month(
        self,
        emp_id: int,
        year: int,
        month: int
    ) -> List[Attendance]:
        """Get attendance records for an employee in a specific month."""
        return self.att_repo.get_by_employee_and_month(emp_id, year, month)

    def list_attendance_by_date_range(
        self,
        emp_id: int,
        start_date: date,
        end_date: date
    ) -> List[Attendance]:
        """Get attendance records in a date range."""
        if start_date > end_date:
            raise InvalidInputError("Start date must be before end date")
        
        return self.att_repo.get_by_date_range(emp_id, start_date, end_date)

    def update_attendance(
        self,
        att_id: int,
        att_update: AttendanceUpdate,
        updated_by: int
    ) -> Attendance:
        """Update attendance record."""
        att = self.get_attendance(att_id)
        
        update_data = att_update.dict(exclude_unset=True)
        update_data["updated_by"] = updated_by
        
        return self.att_repo.update(att_id, update_data)

    def delete_attendance(self, att_id: int) -> bool:
        """Soft delete attendance record."""
        att = self.get_attendance(att_id)
        return self.att_repo.delete(att_id)

    def get_attendance_summary(
        self,
        emp_id: int,
        year: int,
        month: int
    ) -> dict:
        """
        Get attendance summary for an employee for a specific month.
        
        Returns:
            Dictionary with count of present, absent, leave, half_day
        """
        records = self.list_attendance_by_employee_and_month(emp_id, year, month)
        
        summary = {
            "total_days": len(records),
            "present": 0,
            "absent": 0,
            "leave": 0,
            "half_day": 0
        }
        
        for record in records:
            if record.status.value == "present":
                summary["present"] += 1
            elif record.status.value == "absent":
                summary["absent"] += 1
            elif record.status.value == "leave":
                summary["leave"] += 1
            elif record.status.value == "half_day":
                summary["half_day"] += 1
        
        return summary
