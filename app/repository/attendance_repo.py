"""Attendance repository."""

from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Attendance
from app.core.enums import AttendanceStatusEnum
from app.repository.base import BaseRepository


class AttendanceRepository(BaseRepository[Attendance]):
    """Repository for Attendance model."""

    def __init__(self, db: Session):
        super().__init__(db, Attendance)

    def get_by_employee_and_date(
        self,
        employee_id: int,
        attendance_date: date
    ) -> Optional[Attendance]:
        """Get attendance record for specific employee and date."""
        return self.db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.attendance_date == attendance_date
        ).first()

    def get_by_employee(
        self,
        employee_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Attendance]:
        """Get all attendance records for an employee."""
        return self.db.query(Attendance).filter(
            Attendance.employee_id == employee_id
        ).order_by(Attendance.attendance_date.desc()).offset(skip).limit(limit).all()

    def get_by_employee_and_month(
        self,
        employee_id: int,
        year: int,
        month: int
    ) -> List[Attendance]:
        """Get attendance records for an employee in a specific month."""
        return self.db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            func.extract('year', Attendance.attendance_date) == year,
            func.extract('month', Attendance.attendance_date) == month
        ).order_by(Attendance.attendance_date.asc()).all()

    def get_by_date_range(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Attendance]:
        """Get attendance records in a date range."""
        return self.db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date
        ).order_by(Attendance.attendance_date.asc()).all()

    def count_by_employee_and_status(
        self,
        employee_id: int,
        status: AttendanceStatusEnum
    ) -> int:
        """Count attendance records by status."""
        return self.db.query(func.count(Attendance.id)).filter(
            Attendance.employee_id == employee_id,
            Attendance.status == status
        ).scalar()

    def get_by_status(
        self,
        status: AttendanceStatusEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[Attendance]:
        """Get all attendance records with specific status."""
        return self.db.query(Attendance).filter(
            Attendance.status == status
        ).offset(skip).limit(limit).all()
