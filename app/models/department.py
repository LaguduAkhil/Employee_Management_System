"""Department model."""

from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Department(Base):
    """Department model - organizes employees into departments."""

    __tablename__ = "departments"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Basic Info
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    
    # Manager Info (can be null if no manager assigned)
    manager_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True)

    # Status
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
    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name={self.name}, code={self.code})>"
