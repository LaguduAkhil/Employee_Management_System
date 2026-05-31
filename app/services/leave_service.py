"""Leave service for leave management."""

from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import Leave, Employee
from app.repository import LeaveRepository, EmployeeRepository
from app.schemas.leave import LeaveCreate, LeaveUpdate
from app.core.enums import LeaveStatusEnum
from app.utils.exceptions import LeaveNotFoundError, InvalidInputError


class LeaveService:
    """Service layer for leave operations."""

    def __init__(self, db: Session):
        self.db = db
        self.leave_repo = LeaveRepository(db)
        self.emp_repo = EmployeeRepository(db)

    def create_leave_request(
        self,
        emp_id: int,
        leave_create: LeaveCreate
    ) -> Leave:
        """
        Create a new leave request.
        
        Args:
            emp_id: Employee ID
            leave_create: Leave creation request
        
        Returns:
            Created leave request
        
        Raises:
            InvalidInputError: If employee not found or invalid dates
        """
        emp = self.emp_repo.get_by_id(emp_id)
        if not emp or emp.is_deleted:
            raise InvalidInputError(f"Employee {emp_id} not found")

        # Validate dates
        if leave_create.start_date > leave_create.end_date:
            raise InvalidInputError("Start date must be before end date")

        # Validate leave balance (simple check)
        self._validate_leave_balance(emp, leave_create)

        leave_data = {
            "employee_id": emp_id,
            "leave_type": leave_create.leave_type,
            "start_date": leave_create.start_date,
            "end_date": leave_create.end_date,
            "reason": leave_create.reason,
            "number_of_days": leave_create.number_of_days,
            "status": LeaveStatusEnum.PENDING
        }
        return self.leave_repo.create(leave_data)

    def get_leave(self, leave_id: int) -> Leave:
        """Get leave request by ID."""
        leave = self.leave_repo.get_by_id(leave_id)
        if not leave:
            raise LeaveNotFoundError(f"Leave request {leave_id} not found")
        return leave

    def list_leaves_by_employee(
        self,
        emp_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Leave], int]:
        """List all leave requests for an employee."""
        skip = (page - 1) * page_size
        leaves = self.leave_repo.get_by_employee(emp_id, skip=skip, limit=page_size)
        total = len(leaves)  # Can be optimized
        return leaves, total

    def list_pending_leaves(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Leave], int]:
        """List all pending leave requests."""
        skip = (page - 1) * page_size
        leaves = self.leave_repo.get_pending_leaves(skip=skip, limit=page_size)
        total = self.leave_repo.count_pending()
        return leaves, total

    def list_leaves_by_employee_and_status(
        self,
        emp_id: int,
        status: LeaveStatusEnum,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Leave], int]:
        """List leave requests for an employee with specific status."""
        skip = (page - 1) * page_size
        leaves = self.leave_repo.get_by_employee_and_status(
            emp_id,
            status,
            skip=skip,
            limit=page_size
        )
        total = self.leave_repo.count_by_employee_and_status(emp_id, status)
        return leaves, total

    def approve_leave(
        self,
        leave_id: int,
        approved_by: int,
        remarks: Optional[str] = None
    ) -> Leave:
        """
        Approve a leave request.
        
        Args:
            leave_id: Leave request ID
            approved_by: ID of user approving
            remarks: Optional remarks
        
        Returns:
            Updated leave request
        """
        leave = self.get_leave(leave_id)
        
        if leave.status != LeaveStatusEnum.PENDING:
            raise InvalidInputError(f"Can only approve pending leave requests, current status: {leave.status}")

        update_data = {
            "status": LeaveStatusEnum.APPROVED,
            "approved_by": approved_by,
            "approved_at": datetime.now(timezone.utc),
            "remarks": remarks
        }
        return self.leave_repo.update(leave_id, update_data)

    def reject_leave(
        self,
        leave_id: int,
        approved_by: int,
        remarks: str
    ) -> Leave:
        """
        Reject a leave request.
        
        Args:
            leave_id: Leave request ID
            approved_by: ID of user rejecting
            remarks: Reason for rejection
        
        Returns:
            Updated leave request
        """
        leave = self.get_leave(leave_id)
        
        if leave.status != LeaveStatusEnum.PENDING:
            raise InvalidInputError(f"Can only reject pending leave requests, current status: {leave.status}")

        update_data = {
            "status": LeaveStatusEnum.REJECTED,
            "approved_by": approved_by,
            "approved_at": datetime.now(timezone.utc),
            "remarks": remarks
        }
        return self.leave_repo.update(leave_id, update_data)

    def cancel_leave(self, leave_id: int, remarks: Optional[str] = None) -> Leave:
        """Cancel a leave request."""
        leave = self.get_leave(leave_id)
        
        if leave.status not in [LeaveStatusEnum.APPROVED, LeaveStatusEnum.PENDING]:
            raise InvalidInputError(f"Can only cancel pending or approved leaves, current status: {leave.status}")

        update_data = {
            "status": LeaveStatusEnum.CANCELLED,
            "remarks": remarks
        }
        return self.leave_repo.update(leave_id, update_data)

    def _validate_leave_balance(self, emp: Employee, leave_create: LeaveCreate) -> None:
        """Validate that employee has sufficient leave balance."""
        leave_type = leave_create.leave_type.value
        
        if leave_type == "casual":
            if emp.casual_leaves < leave_create.number_of_days:
                raise InvalidInputError(f"Insufficient casual leave balance. Available: {emp.casual_leaves}")
        elif leave_type == "sick":
            if emp.sick_leaves < leave_create.number_of_days:
                raise InvalidInputError(f"Insufficient sick leave balance. Available: {emp.sick_leaves}")
        elif leave_type == "earned":
            if emp.earned_leaves < leave_create.number_of_days:
                raise InvalidInputError(f"Insufficient earned leave balance. Available: {emp.earned_leaves}")
