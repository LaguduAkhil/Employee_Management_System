"""Attendance model."""

from datetime import datetime, date
from sqlalchemy import DateTime, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AttendanceStatusEnum
from app.db.database import Base


class Attendance(Base):
    """Attendance model - tracks daily employee attendance."""

    __tablename__ = "attendance"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign Keys
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)

    # Attendance Details
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatusEnum] = mapped_column(nullable=False)
    
    # Optional check-in/out times
    check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    created_by: Mapped[int] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[int] = mapped_column(Integer, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="attendance_records",
        foreign_keys=[employee_id]
    )

    def __repr__(self) -> str:
        return f"<Attendance(id={self.id}, employee_id={self.employee_id}, date={self.attendance_date}, status={self.status})>"
