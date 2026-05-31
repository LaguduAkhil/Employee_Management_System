"""Employee model."""

from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import EmployeeStatusEnum
from app.db.database import Base


class Employee(Base):
    """Employee model - stores employee information and department assignment."""

    __tablename__ = "employees"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)

    # Employee Details
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    date_of_joining: Mapped[date] = mapped_column(Date, nullable=True)
    
    # Leave Balance
    casual_leaves: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    sick_leaves: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    earned_leaves: Mapped[int] = mapped_column(Integer, default=20, nullable=False)

    # Status
    employment_status: Mapped[EmployeeStatusEnum] = mapped_column(
        default=EmployeeStatusEnum.ACTIVE,
        nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

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
    user: Mapped["User"] = relationship(
        "User",
        back_populates="employee",
        foreign_keys=[user_id]
    )
    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="employees",
        foreign_keys=[department_id]
    )
    leaves: Mapped[list["Leave"]] = relationship(
        "Leave",
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    attendance_records: Mapped[list["Attendance"]] = relationship(
        "Attendance",
        back_populates="employee",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, code={self.employee_code}, name={self.first_name} {self.last_name})>"
