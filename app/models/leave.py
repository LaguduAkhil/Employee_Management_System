"""Leave request model."""

from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import LeaveStatusEnum, LeaveTypeEnum
from app.db.database import Base


class Leave(Base):
    """Leave model - tracks leave requests and approvals."""

    __tablename__ = "leaves"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign Keys
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)

    # Leave Details
    leave_type: Mapped[LeaveTypeEnum] = mapped_column(nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    number_of_days: Mapped[float] = mapped_column(nullable=False)

    # Status
    status: Mapped[LeaveStatusEnum] = mapped_column(
        default=LeaveStatusEnum.PENDING,
        nullable=False,
        index=True
    )
    remarks: Mapped[str] = mapped_column(Text, nullable=True)

    # Approval Info
    approved_by: Mapped[int] = mapped_column(Integer, nullable=True)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

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

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="leaves",
        foreign_keys=[employee_id]
    )

    def __repr__(self) -> str:
        return f"<Leave(id={self.id}, employee_id={self.employee_id}, status={self.status})>"
