"""
Enums for the Employee Management System.
Defines all role and status types used across the application.
"""

from enum import Enum


class RoleEnum(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class LeaveStatusEnum(str, Enum):
    """Leave request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveTypeEnum(str, Enum):
    """Types of leave available."""
    SICK = "sick"
    CASUAL = "casual"
    EARNED = "earned"
    UNPAID = "unpaid"


class AttendanceStatusEnum(str, Enum):
    """Employee attendance status."""
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"
    HALF_DAY = "half_day"


class EmployeeStatusEnum(str, Enum):
    """Employee employment status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    RESIGNED = "resigned"
